class AIService:

    @staticmethod
    def generate_summary(report):

        return {

            "executive_summary":
            f"The uploaded dataset contains {report['rows']} rows and {report['columns']} columns.",

            "key_insights":[
                "Dataset uploaded successfully.",
                f"Found {report['missing_values']} missing values.",
                f"Found {report['duplicate_rows']} duplicate rows."
            ],

            "recommendations":[
                "Clean missing values.",
                "Remove duplicate rows.",
                "Create business dashboards."
            ],

            "business_risks":[
                "Poor data quality may affect decisions."
            ],

            "opportunities":[
                "Generate KPI dashboard.",
                "Predict future sales using AI."
            ]
        }