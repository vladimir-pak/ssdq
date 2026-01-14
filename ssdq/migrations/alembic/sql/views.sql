--
-- PostgreSQL database dump
--

-- Dumped from database version 14.12
-- Dumped by pg_dump version 14.12

--
-- Name: view_all_controls_bymonth; Type: VIEW; Schema: ssdq; Owner: ssdq
--

CREATE OR REPLACE VIEW ssdq.view_all_controls_bymonth AS
 WITH calendar AS (
         SELECT (gs.gs)::date AS thedate
           FROM generate_series((date_trunc('month'::text, (CURRENT_DATE - '11 mons'::interval)))::timestamp with time zone, date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone), '1 mon'::interval) gs(gs)
        ), controls AS (
            SELECT ch.id,
            ch.status_id,
            ch.team_id,
            ch.effective_from,
            ch.effective_to,
            row_number() over(partition by ch.id, date_trunc('month'::text, ch.effective_from) order by ch.effective_from desc) as rn
            FROM ssdq.dq_control_hist ch
        )
 SELECT c.thedate,
    COALESCE(ct.id, -1) AS id,
    ct.team_id,
    ct.status_id
   FROM calendar c
     LEFT JOIN controls ct ON c.thedate >= date_trunc('month'::text, ct.effective_from) and c.thedate < ct.effective_to and ct.rn = 1
  ORDER BY c.thedate;



--
-- Name: view_controls_error_bymonth; Type: VIEW; Schema: ssdq; Owner: ssdq
--

CREATE OR REPLACE VIEW ssdq.view_controls_error_bymonth AS
 WITH calendar AS (
         SELECT (gs.gs)::date AS thedate
           FROM generate_series((date_trunc('month'::text, (CURRENT_DATE - '11 mons'::interval)))::timestamp with time zone, date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone), '1 mon'::interval) gs(gs)
        ), controls AS (
         SELECT date(agg.report_date) AS report_date,
            agg.control_id,
            c.team_id
           FROM ssdq.dq_detail_agg agg
             JOIN ssdq.dq_control_sdim c ON agg.control_id = c.id AND c.deleted_flag::bpchar = 'N'::bpchar
          WHERE agg.mistake_count > (0)::numeric
        )
 SELECT cal.thedate AS report_date,
    COALESCE(c.control_id, ('-1'::integer)::numeric) AS id,
    c.team_id AS team_id
   FROM calendar cal
     LEFT JOIN controls c ON cal.thedate <= c.report_date AND (cal.thedate + '1 mon'::interval) > c.report_date;


--
-- Name: view_controls_last_results; Type: VIEW; Schema: ssdq; Owner: ssdq
--

CREATE OR REPLACE VIEW ssdq.view_controls_last_results
AS WITH agg AS (
         SELECT t.control_id,
            t.pm_workflow_run_id,
            t.mistake_count,
            t.end_time,
            t.error_flag,
            t.rn
           FROM ( SELECT ag.control_id,
                    ag.pm_workflow_run_id,
                    ag.mistake_count,
                    ag.end_time,
                    ag.error_flag,
                    row_number() OVER (PARTITION BY ag.control_id ORDER BY ag.pm_workflow_run_id desc) AS rn
                   FROM ssdq.dq_detail_agg ag) t
          WHERE t.rn = 1
        )
 SELECT c.id,
    agg.pm_workflow_run_id,
    agg.mistake_count,
    agg.end_time,
    agg.error_flag,
    c.status_id
   FROM ssdq.dq_control_sdim c
     LEFT JOIN agg ON c.id = agg.control_id
  WHERE c.deleted_flag::text = 'N'::text;


CREATE OR REPLACE VIEW ssdq.dq_detailjournal_view
AS SELECT dt.control_id,
    dt.report_time,
    dt.xk,
    dt.pm_workflow_run_id,
    dt."json",
    t.name AS group_id
   FROM ssdq.dq_detailjournal_web dt
     JOIN ssdq.dq_control_sdim c ON dt.control_id = c.id AND c.deleted_flag::text <> 'Y'::text
     JOIN ssdq_admin.teams t ON c.team_id = t.id;
