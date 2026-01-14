from flask import request
from flask_login import current_user
from ...app.extensions import db
from ...models.base import dq_detail_agg, dq_detailjournal_web, dq_jira_issues
from ...models.dict import error_reason_sdim
from ...logger.log import LogEvent
from sqlalchemy import String, and_, or_, func


def validate_json_attributes(json_keys:list[str]) -> bool:
    try:
        for cur in json_keys:
            if ' ' in cur:
                return False
        return True
    except Exception as ex:
        LogEvent.log_error(ex)
        return False
    

class Report:
    def __init__(self, id:int, wf_id:int|None=None):
        self.control_id = id
        if not wf_id:
            if request.method == "POST":
                self.wf_id = int(request.form["wfId"]) if request.form["wfId"] else 0
            else:
                self.wf_id = int(request.args.get("wfId")) if request.args.get("wfId") else 0
        else:
            self.wf_id = wf_id

    def agg_report(self):
        try:
            report = db.session.query(
                dq_detail_agg.report_date,
                dq_detail_agg.pm_workflow_run_id,
                dq_detail_agg.mistake_count
            ).filter_by(
                control_id=self.control_id
            ).order_by(
                dq_detail_agg.report_date.desc()
            ).all()

            if not report:
                raise Exception("There is no report")
            else:
                report = dict(
                    report_date=[row.report_date.strftime('%Y-%m-%d %H:%M:%S') for row in report],
                    wf_id=[row.pm_workflow_run_id for row in report],
                    mistake_count=[row.mistake_count for row in report]
                )
            
            response = dict(
                control_id=self.control_id,
                report=report
            )
            return response
                
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
    
    def detail_report(self):
        try:
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            if request.form.get('order[0][column]'):
                order_id = int(request.form['order[0][column]'])
                order_dir = request.form['order[0][dir]']
            else:
                order_id = 0
                order_dir = 'asc'
            draw = request.form['draw']
            
            """Cheking results by workflow id"""
            json_data = db.session.query(dq_detailjournal_web.json).filter_by(
                control_id=self.control_id,
                pm_workflow_run_id=self.wf_id
            ).first()
            
            if json_data:
                column_list = list(json_data.json.keys())
                if not validate_json_attributes(column_list):
                    return {
                        'draw': 1,
                        'iTotalRecords': 0,
                        'iTotalDisplayRecords': 0,
                        'aaData': [],
                        'headers': [],
                        'error_message': 'Некорректный атрибутный состав'
                    }
            else:
                error_message = db.session.query(dq_detail_agg.error_name).filter_by(
                    control_id=self.control_id,
                    pm_workflow_run_id=self.wf_id
                ).first()
                return {
                    'draw': 1,
                    'iTotalRecords': 0,
                    'iTotalDisplayRecords': 0,
                    'aaData': [],
                    'headers': [],
                    'error_message': (error_message.error_name if error_message else None)
                }
            order = dq_detailjournal_web.json[column_list[int(order_id)]].cast(String).desc() if order_dir == "desc" \
                else dq_detailjournal_web.json[column_list[int(order_id)]].cast(String)

            total_records = self.get_total_records()
            total_record_filtered = total_records

            data = self.get_dataset(row=row, rowperpage=rowperpage, order=order)
            response = {
                'draw': draw,
                'iTotalRecords': total_records,
                'iTotalDisplayRecords': total_record_filtered,
                'aaData': data,
                'headers': column_list
            }
            return response
            
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex

    def get_total_records(self):
        data = db.session.query(
            dq_detail_agg.mistake_count
        ).filter_by(
            control_id=self.control_id,
            pm_workflow_run_id=self.wf_id
        ).first()
        response = int(data.mistake_count)

        return response
    
    def get_dataset(self, **kwargs):
        report = db.session.query(
            dq_detailjournal_web.json
        ).filter(
            dq_detailjournal_web.control_id == self.control_id,
            dq_detailjournal_web.pm_workflow_run_id == self.wf_id
        ).order_by(kwargs["order"]).limit(int(kwargs["rowperpage"])).offset(int(kwargs["row"])).all()

        return [
            [value for key, value in cur.json.items()]
                for cur in report]

    def get_jira_data(self):
        try:
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            if request.form.get('order[0][column]'):
                order_id = int(request.form['order[0][column]'])
                order_dir = request.form['order[0][dir]']
            else:
                order_id = 4
                order_dir = 'asc'
            draw = request.form['draw']
            
            """Cheking results by workflow id"""
            json_data = db.session.query(dq_detailjournal_web.json).filter_by(
                control_id=self.control_id,
                pm_workflow_run_id=self.wf_id
            ).first()
            if json_data:
                column_list = list(json_data.json.keys())
                if not validate_json_attributes(column_list):
                    return {
                        'draw': 1,
                        'iTotalRecords': 0,
                        'iTotalDisplayRecords': 0,
                        'aaData': [],
                        'headers': []
                    }
            else:
                return {
                    'draw': 1,
                    'iTotalRecords': 0,
                    'iTotalDisplayRecords': 0,
                    'aaData': [],
                    'headers': []
                }
            
            attr_list = column_list + ["jira_issue", "json", "error_reason", "pm_workflow_run_id", "xk"]
            
            columns_order = [
                dq_jira_issues.jira_issue,
                dq_jira_issues.json["error_origin"].cast(String),
                dq_jira_issues.json["error_reason"].cast(String),
                dq_detailjournal_web.pm_workflow_run_id,
                dq_detailjournal_web.xk
                ] + [dq_detailjournal_web.json[col].cast(String) for col in column_list]
            order = columns_order[int(order_id)].desc() if order_dir == "desc" \
                else columns_order[int(order_id)]
                
            total_records = self.get_total_records()
            total_record_filtered = total_records
            
            dataset = dq_detailjournal_web.query.join(
                dq_jira_issues, 
                and_(dq_jira_issues.pm_workflow_run_id == dq_detailjournal_web.pm_workflow_run_id,
                    dq_jira_issues.xk == dq_detailjournal_web.xk),
                isouter=True
            ).join(
                error_reason_sdim,
                and_(
                    # error_reason_sdim.id == dq_jira_issues.json["error_reason"].cast(String),
                    error_reason_sdim.id.cast(String) == func.substring(dq_jira_issues.json["error_reason"].cast(String), 2, 36),
                    error_reason_sdim.deleted_flag == "N"
                ),
                isouter=True
            ).add_columns(
                dq_jira_issues.jira_issue,
                dq_jira_issues.json,
                error_reason_sdim.name.label("error_reason"),
                dq_detailjournal_web.pm_workflow_run_id,
                dq_detailjournal_web.xk,
                # *[DetailJournal.attributes[ind] for ind in DetailJournal.attributes]
                *[dq_detailjournal_web.json[cur].label(cur) for cur in column_list]
            ).filter(
                dq_detailjournal_web.control_id == self.control_id,
                dq_detailjournal_web.pm_workflow_run_id == self.wf_id
            ).order_by(order).limit(int(rowperpage)).offset(int(row)).all()
                
            data = []
            for row in dataset:
                krow = {}
                krow["rowId"] = row.xk
                for key in attr_list:
                    krow[key] = getattr(row, key)
                data.append(krow)
            
            response = {
                'draw': draw,
                'iTotalRecords': total_records,
                'iTotalDisplayRecords': total_record_filtered,
                'aaData': data,
                'headers': column_list
            }
            return response
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex


class ReportJira:
    def __init__(self):
        self.entity_name = "Инцидент"
        self.entity_name_eng = "Incident"
        self.attr_form = ['xk', 'jira_issue']
        self.json_attr = ['error_origin', 'error_reason']

        self.values, self.json = {}, {}
        for ind in self.attr_form:
            self.values[ind] = request.form.get(ind)
        
        for ind in self.json_attr:
            self.json[ind] = request.form.get(ind)
            
    def add(self, control_id:int, wf_id:int):
        try:
            query = db.session.query(
                dq_jira_issues.pm_workflow_run_id,
                dq_jira_issues.xk
            )
            
            rows = request.form.getlist('rowsId[]')
            if rows:
                rows = list(map(int, rows))
                query = query.filter(
                    dq_jira_issues.pm_workflow_run_id == wf_id,
                    dq_jira_issues.xk.in_(rows)
                )
            else:
                rows = [int(row.xk) for row in db.session.query(dq_detailjournal_web.xk).filter_by(
                    control_id=control_id,
                    pm_workflow_run_id=wf_id
                ).all()]
                query = query.filter_by(
                    pm_workflow_run_id=wf_id
                )
            is_exist = query.all()
            
            xk_list = [int(row.xk) for row in is_exist]
            
            if xk_list:
                self.update_bulk(wf_id=wf_id, xk_list=xk_list)
                new_xk = []
                for row in rows:
                    if row in xk_list:
                        continue
                    new_xk.append(row)
            else:
                new_xk = rows
            
            if new_xk:
                issues = [dq_jira_issues(pm_workflow_run_id=wf_id, xk=row, json=self.json)
                        for row in new_xk]
                db.session.add_all(issues)
                db.session.commit()
            
            for cur in new_xk:
                LogEvent.log_event(eventName="createEntity", entityName=self.entity_name_eng, entityId=cur)
            response = {'message': f'{self.entity_name} добавлен!'}
            return response, 204
        except Exception as ex:
            LogEvent.log_error(ex)
            return {"response": "error occured"}, 500
        
    def update(self, wf_id:int, xk:int|None=None):
        issue = dq_jira_issues.query.filter_by(
            pm_workflow_run_id=wf_id,
            xk=xk
        ).update(
            dict(
                json=self.json,
            )
        )
        db.session.commit()

        LogEvent.log_event(eventName="updateEntity", entityName=self.entity_name_eng, entityId=xk)
        response = {'message': f'{self.entity_name} изменен!'}
        return response, 204
    
    def update_bulk(self, wf_id:int, xk_list:list[int]):
        update = dq_jira_issues.query.filter(
            dq_jira_issues.pm_workflow_run_id == wf_id,
            dq_jira_issues.xk.in_(xk_list)
        ).update(
            dict(
                json=self.json,
            )
        )
        db.session.commit()
        for cur in xk_list:
            LogEvent.log_event(eventName="updateEntity", entityName=self.entity_name_eng, entityId=cur)
        return None

    def delete(self, wf_id:int):
        issue = dq_jira_issues.query.filter_by(
            pm_workflow_run_id=wf_id,
            xk=self.values['xk']
        ).update(dict(
            json=dict(
                error_origin=None,
                error_reason=None
            )
        ))
        db.session.commit()

        LogEvent.log_event(eventName="deleteEntity", entityName=self.entity_name_eng, entityId=self.values['xk'])
        response = {'message': f'{self.entity_name} удален!'}
        return response, 204
    
    @staticmethod
    def get_data(control_id:int, wf_id:int):
        try:
            error_reasons = error_reason_sdim.query.filter_by(
                team_id=current_user.team_id,
                deleted_flag="N"
            ).all()
            error_reasons_dict = [dict(
                id=row.id,
                name=row.name
            ) for row in error_reasons]
            
            jira_data = db.session.query(
                dq_jira_issues.jira_issue
            ).filter_by(
                pm_workflow_run_id=wf_id,
                xk=0
            ).first()
            jira_issue = jira_data.jira_issue if jira_data else None
            json_result = db.session.query(
                dq_detailjournal_web.json
            ).filter_by(
                control_id=control_id,
                pm_workflow_run_id=wf_id
            ).first()
            columns = list(json_result.json.keys()) if json_result else []
            
            response = dict(
                error_reason=error_reasons_dict,
                jira_issue=jira_issue,
                columns=columns
            )
            return response
        
        except Exception as ex:
            LogEvent.log_error(ex)
            raise ex
        