# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns() -> list[dict]:
    """Return columns for the report.

    Education v16's Assessment Result / Plan carry no company, so this is per stream (student group).
    """
    return [
        {"label": "Stream", "fieldname": "stream", "fieldtype": "Data", "width": 200},
        {
            "label": "Average %",
            "fieldname": "average_percentage",
            "fieldtype": "Float",
            "width": 150,
            "precision": 1,
        },
    ]


def get_data(filters) -> list[list]:
    filters = filters or {}
    conditions = get_conditions(filters)

    data = frappe.db.sql(
        """
        SELECT
            ap.student_group AS stream,
            ROUND(AVG(ar.total_score / ar.maximum_score * 100), 1) AS average_percentage
        FROM
            `tabAssessment Result` ar
        JOIN
            `tabAssessment Plan` ap ON ap.name = ar.assessment_plan
        WHERE
            ar.total_score IS NOT NULL
            AND ar.maximum_score
            AND ar.docstatus != 2
            {conditions}
        GROUP BY
            ap.student_group
        ORDER BY
            ap.student_group
    """.format(
            conditions=conditions
        ),
        filters,
        as_dict=True,
    )

    return data


def get_chart(data):
    if not data:
        return None

    return {
        "data": {
            "labels": [d.stream for d in data],
            "datasets": [{"name": _("Average %"), "values": [d.average_percentage for d in data]}],
        },
        "type": "bar",
        "title": _("Average Performance by Stream"),
    }


def get_conditions(filters):
    conditions = ""
    if filters.get("academic_year"):
        conditions += " AND ar.academic_year = %(academic_year)s"
    if filters.get("academic_term"):
        conditions += " AND ar.academic_term = %(academic_term)s"

    return conditions
