
import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

def make_chart(budget):
    labels = list(budget.keys())[:-1]
    values = list(budget.values())[:-1]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_ylabel("Estimated Cost (INR)")
    ax.set_title("Trip Budget Breakdown")
    ax.tick_params(axis="x", labelrotation=25)
    fig.tight_layout()

    output = io.BytesIO()
    fig.savefig(output, format="png")
    plt.close(fig)
    output.seek(0)
    return output

def make_pdf(trip, itinerary, budget):
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("Smart Trip Planner", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            f"Traveler: {trip['traveler_name']}",
            styles["Normal"]
        ),
        Paragraph(
            f"Destination: {trip['destination']}",
            styles["Normal"]
        ),
        Paragraph(
            f"Start Date: {trip['start_date']}",
            styles["Normal"]
        ),
        Paragraph(
            f"Duration: {trip['duration_days']} days",
            styles["Normal"]
        ),
        Spacer(1, 12),
        Paragraph("Estimated Budget", styles["Heading2"])
    ]

    for name, amount in budget.items():
        content.append(
            Paragraph(f"{name}: Rs. {amount:,.0f}", styles["Normal"])
        )

    content.append(Spacer(1, 12))
    content.append(
        Paragraph("Day-wise Itinerary", styles["Heading2"])
    )

    for day in itinerary:
        content.append(
            Paragraph(f"Day {day['day']}", styles["Heading3"])
        )
        content.append(
            Paragraph(f"Morning: {day['morning']}", styles["Normal"])
        )
        content.append(
            Paragraph(f"Afternoon: {day['afternoon']}", styles["Normal"])
        )
        content.append(
            Paragraph(f"Evening: {day['evening']}", styles["Normal"])
        )
        content.append(Spacer(1, 8))

    doc.build(content)
    output.seek(0)
    return output
