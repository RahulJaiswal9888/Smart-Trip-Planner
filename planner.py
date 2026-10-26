import json
import numpy as np

DESTINATIONS = {
    "Manali": [
        "Hadimba Temple",
        "Old Manali",
        "Solang Valley",
        "Mall Road",
        "Vashisht"
    ],
    "Shimla": [
        "The Ridge",
        "Mall Road",
        "Jakhoo Temple",
        "Kufri",
        "Christ Church"
    ],
    "Jaipur": [
        "Amber Fort",
        "Hawa Mahal",
        "City Palace",
        "Jantar Mantar",
        "Johari Bazaar"
    ],
    "Amritsar": [
        "Golden Temple",
        "Jallianwala Bagh",
        "Partition Museum",
        "Hall Bazaar",
        "Wagah Border"
    ],
    "Udaipur": [
        "City Palace",
        "Lake Pichola",
        "Jagdish Temple",
        "Saheliyon Ki Bari",
        "Fateh Sagar Lake"
    ],
    "Rishikesh": [
        "Ram Jhula",
        "Triveni Ghat",
        "Beatles Ashram",
        "Neer Garh Waterfall",
        "Ganga Aarti"
    ]
}

HOTELS = {
    "Manali": {"Budget": 1800, "Standard": 3200, "Luxury": 5500},
    "Shimla": {"Budget": 2000, "Standard": 3500, "Luxury": 6000},
    "Jaipur": {"Budget": 1600, "Standard": 3000, "Luxury": 5200},
    "Amritsar": {"Budget": 1500, "Standard": 2800, "Luxury": 4800},
    "Udaipur": {"Budget": 1900, "Standard": 3300, "Luxury": 5800},
    "Rishikesh": {"Budget": 1700, "Standard": 3100, "Luxury": 5200}
}


def _style_plan(places, style):
    """Return a place ordering that matches the selected travel style."""
    if style == "Adventure":
        # Put more activity-friendly/nature spots earlier.
        preferred_words = (
            "Solang", "Kufri", "Neer Garh", "Ram Jhula",
            "Amber", "Wagah"
        )
        return sorted(
            places,
            key=lambda p: next(
                (i for i, word in enumerate(preferred_words) if word.lower() in p.lower()),
                len(preferred_words)
            )
        )

    if style == "Relaxed":
        # Prefer calmer/local sightseeing before busier highlights.
        relaxed_words = (
            "Old Manali", "Vashisht", "Saheliyon", "Fateh",
            "Christ Church", "Lake Pichola", "Triveni"
        )
        return sorted(
            places,
            key=lambda p: next(
                (i for i, word in enumerate(relaxed_words) if word.lower() in p.lower()),
                len(relaxed_words)
            )
        )

    if style == "Luxury":
        # Put major landmark/heritage experiences first.
        luxury_words = (
            "City Palace", "Amber Fort", "Golden Temple",
            "Lake Pichola", "Hadimba", "Christ Church"
        )
        return sorted(
            places,
            key=lambda p: next(
                (i for i, word in enumerate(luxury_words) if word.lower() in p.lower()),
                len(luxury_words)
            )
        )

    # Budget and Standard use the original destination order.
    return list(places)


def generate_itinerary(destination, days, style):
    """
    Generate a destination-specific day-wise itinerary.

    The existing app.py expects each item to contain:
    day, morning, afternoon, evening and style.
    """
    if destination not in DESTINATIONS:
        raise ValueError(f"Unknown destination: {destination}")

    days = int(days)
    if days < 1:
        raise ValueError("Trip duration must be at least 1 day.")

    places = _style_plan(DESTINATIONS[destination], style)
    itinerary = []

    # Use every destination place once before repeating any place.
    # This keeps short trips varied and still supports longer trips.
    schedule = []
    while len(schedule) < days * 3:
        schedule.extend(places)

    schedule = schedule[:days * 3]

    for day in range(days):
        morning = schedule[day * 3]
        afternoon = schedule[day * 3 + 1]
        evening = schedule[day * 3 + 2]

        itinerary.append({
            "day": day + 1,
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "style": style
        })

    return itinerary


def calculate_budget(destination, days, people, hotel_type, travel_cost):
    if destination not in HOTELS:
        raise ValueError(f"Unknown destination: {destination}")

    if hotel_type not in HOTELS[destination]:
        hotel_type = "Standard"

    days = max(int(days), 1)
    people = max(int(people), 1)

    hotel_rate = HOTELS[destination][hotel_type]

    # Hotel is charged for nights, not days.
    hotel_nights = max(days - 1, 1)
    hotel_cost = hotel_rate * hotel_nights

    food_cost = 600 * days * people
    local_transport = 400 * days * people
    travel_cost = float(travel_cost)

    subtotal = (
        hotel_cost
        + food_cost
        + local_transport
        + travel_cost
    )

    buffer = float(np.ceil(subtotal * 0.10))
    total = subtotal + buffer

    return {
        "Hotel": hotel_cost,
        "Food": food_cost,
        "Local Transport": local_transport,
        "Travel": travel_cost,
        "Extra Buffer": buffer,
        "Total": total
    }


def itinerary_json(itinerary):
    return json.dumps(itinerary, ensure_ascii=False)
