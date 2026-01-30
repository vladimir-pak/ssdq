from datetime import datetime, date
from sqlalchemy import asc, desc, and_, or_, cast, func, String, Boolean
from flask import jsonify, request, Response, stream_with_context
from ...app.extensions import db
import io
import csv


class AGGrid:
    """
    obj: ORM-модель
    allowed_cols: dict[str, sqlalchemy column]  (colId -> column)
    """
    def __init__(self, obj, allowed_cols: dict, text_ops: set, date_ops: set, set_ops: set | None = None, base_query_fn = None):
        self.obj = obj
        self.ALLOWED_COLS = allowed_cols
        self.TEXT_OPS = text_ops
        self.DATE_OPS = date_ops
        self.SET_OPS = set_ops or set()
        self.base_query_fn = base_query_fn

    def _apply_sort(self, query, sort_model: list):
        for s in (sort_model or []):
            col_id = s.get("colId")
            direction = (s.get("sort") or "asc").lower()
            col = self.ALLOWED_COLS.get(col_id)
            if col is None:
                continue
            query = query.order_by(asc(col) if direction == "asc" else desc(col))
        return query

    def _parse_iso_date(self, val: str) -> date:
        return datetime.fromisoformat(val).date()

    def _apply_filters(self, query, filter_model: dict):
        filter_model = filter_model or {}
        conditions = []

        for col_id, f in filter_model.items():
            col = self.ALLOWED_COLS.get(col_id)
            if col is None:
                continue

            ftype = (f.get("filterType") or "").lower()
            
            if isinstance(col.type, Boolean):
                op = (f.get("type") or "equals")

                if op == "blank":
                    conditions.append(col.is_(None))
                    continue
                if op == "notBlank":
                    conditions.append(col.is_not(None))
                    continue

                raw = f.get("filter")
                if raw is None:
                    continue

                val = str(raw).lower()
                if val in ("true", "1", "yes", "y", "да"):
                    conditions.append(col.is_(True))
                elif val in ("false", "0", "no", "n", "нет"):
                    conditions.append(col.is_(False))
                else:
                    continue

                continue

            # TEXT
            if ftype == "text":
                op = (f.get("type") or "contains")
                
                if op not in self.TEXT_OPS:
                    op = "contains"

                if op == "blank":
                    conditions.append(or_(col.is_(None), col == ""))
                    continue
                if op == "notBlank":
                    conditions.append(and_(col.is_not(None), col != ""))
                    continue

                val = f.get("filter")
                if val is None or val == "":
                    continue

                col_expr = cast(col, String) if col_id == "id" else col
                v = str(val).lower()

                if op == "contains":
                    conditions.append(func.lower(col_expr).like(f"%{v}%"))
                elif op == "notContains":
                    conditions.append(~func.lower(col_expr).like(f"%{v}%"))
                elif op == "equals":
                    conditions.append(func.lower(col_expr) == v)
                elif op == "notEqual":
                    conditions.append(func.lower(col_expr) != v)
                elif op == "startsWith":
                    conditions.append(func.lower(col_expr).like(f"{v}%"))
                elif op == "endsWith":
                    conditions.append(func.lower(col_expr).like(f"%{v}"))

            # DATE
            elif ftype == "date":
                op = (f.get("type") or "equals")
                if op not in self.DATE_OPS:
                    op = "equals"

                if op == "blank":
                    conditions.append(col.is_(None))
                    continue
                if op == "notBlank":
                    conditions.append(col.is_not(None))
                    continue

                date_from = f.get("dateFrom") or f.get("filter")
                date_to = f.get("dateTo") or f.get("filterTo")
                if not date_from:
                    continue

                d1 = self._parse_iso_date(date_from)
                col_date = func.date(col)

                if op == "equals":
                    conditions.append(col_date == d1)
                elif op == "lessThan":
                    conditions.append(col_date < d1)
                elif op == "greaterThan":
                    conditions.append(col_date > d1)
                elif op == "inRange" and date_to:
                    d2 = self._parse_iso_date(date_to)
                    conditions.append(and_(col_date >= d1, col_date <= d2))

        if conditions:
            query = query.filter(and_(*conditions))
        return query

    def _build_query(self, base_filters: dict | None, filter_model: dict, sort_model: list, payload: dict):
        # 1) базовый query: либо ваш кастомный, либо простой
        query = self.base_query_fn(payload) if self.base_query_fn else db.session.query(self.obj)

        if isinstance(query, tuple):
            q, allowed_cols = query
            self.ALLOWED_COLS = allowed_cols
        else:
            q = query if query is not None else db.session.query(self.obj)
            
        # 2) базовые фильтры (teamId и т.п.) — применяем к expressions
        if base_filters:
            clauses = []
            for payload_key, col_expr in base_filters.items():
                val = payload.get(payload_key)
                if val is None:
                    continue
                clauses.append(col_expr == val)
            if clauses:
                q = q.filter(and_(*clauses))

        # 3) фильтры/сортировка
        q = self._apply_filters(q, filter_model)
        q = self._apply_sort(q, sort_model)
        return q

    def _serialize_row(self, row) -> dict:
        out = {}

        # Если это Row (join/add_columns), берём из mapping
        mapping = getattr(row, "_mapping", None)

        for field in self.ALLOWED_COLS.keys():
            if mapping is not None:
                val = mapping.get(field)
            else:
                val = getattr(row, field, None)

            if field == "id" and val is not None:
                out[field] = str(val)
            elif isinstance(val, datetime):
                out[field] = val.isoformat()
            else:
                out[field] = val

        return out

    def get_grid(self, base_filters: dict | None = None):
        payload = request.get_json(force=True) or {}

        start_row = int(payload.get("startRow", 0))
        end_row = int(payload.get("endRow", start_row + 25))
        page_size = max(1, end_row - start_row)

        sort_model = payload.get("sortModel", [])
        filter_model = payload.get("filterModel", {})

        q = self._build_query(base_filters, filter_model, sort_model, payload)

        total_filtered = q.count()
        rows = q.offset(start_row).limit(page_size).all()

        data = [self._serialize_row(r) for r in rows]

        return jsonify({"rows": data, "lastRow": total_filtered})

    def _csv_value(self, row, field: str):
        mapping = getattr(row, "_mapping", None)
        val = mapping.get(field) if mapping is not None else getattr(row, field, None)

        if val is None:
            return ""
        if field == "id":
            return str(val)
        if isinstance(val, datetime):
            return val.isoformat()
        return str(val)

    def export_csv_stream(self, filename: str, base_filters: dict | None = None):
        payload = request.get_json(force=True) or {}

        filter_model = payload.get("filterModel", {})
        sort_model = payload.get("sortModel", [])
        visible_cols = payload.get("visibleCols")

        q = self._build_query(base_filters, filter_model, sort_model, payload)
        q = q.execution_options(stream_results=True)
        
        all_fields = list(self.ALLOWED_COLS.keys())
        if isinstance(visible_cols, list) and visible_cols:
            fields = [f for f in all_fields if f in visible_cols]
        else:
            fields = all_fields

        @stream_with_context
        def generate():
            buf = io.StringIO()
            writer = csv.writer(buf)

            writer.writerow(fields)
            yield buf.getvalue()
            buf.seek(0); buf.truncate(0)

            try:
                for obj in q.yield_per(2000):
                    writer.writerow([self._csv_value(obj, f) for f in fields])
                    if buf.tell() >= 64 * 1024:
                        yield buf.getvalue()
                        buf.seek(0); buf.truncate(0)

                if buf.tell():
                    yield buf.getvalue()
            finally:
                db.session.remove()

        headers = {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        }
        return Response(generate(), headers=headers)
    
    def get_field_values(self, base_filters: dict | None = None, *,
                         distinct: bool = True,
                         limit: int | None = None):
        """
        Возвращает значения одного поля (colId) по текущим фильтрам/сортировке.
        Ожидает JSON payload:
          - field: str (colId)
          - filterModel: dict
          - sortModel: list
          - (опционально) distinct, limit

        distinct=True: вернёт уникальные значения
        limit: ограничение на количество значений
        """

        payload = request.get_json(force=True) or {}
        
        sort_model = payload.get("sortModel", [])
        filter_model = payload.get("filterModel", {})

        field = payload.get("field")
        if not field:
            return jsonify({"error": "field is required"}), 400
        
        q = self._build_query(base_filters, filter_model, sort_model, payload)

        col_expr = self.ALLOWED_COLS.get(field)
        if col_expr is None:
            return jsonify({"error": f"field '{field}' is not allowed"}), 400

        q = q.with_entities(col_expr)

        if distinct:
            q = q.distinct()

        if limit is not None:
            q = q.limit(int(limit))

        rows = q.all()

        values = []
        for (v,) in rows:
            if isinstance(v, datetime):
                values.append(v.isoformat())
            else:
                values.append(v)

        return jsonify({"field": field, "values": values})
    