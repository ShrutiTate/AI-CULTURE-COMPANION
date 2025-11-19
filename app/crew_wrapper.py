import os
from app.agents import (
    generate_culture_summary,
    chat_with_persona,
)
from app.utils import now_iso, fetch_google_search_results


class CultureCrew:
    def get_related_resources(self, place):
        """
        Fetch dynamic resources for a given place using Google Custom Search API.

        Args:
            place (str): The name of the place (country, city, or region).

        Returns:
            list: A list of dictionaries with 'title' and 'url'.
        """
        from app.agents import filter_resource_links

        api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        search_engine_id = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")

        if not api_key or not search_engine_id:
            print("Google Custom Search API credentials are missing.")
            return []

        # Refined query for best relevance
        query = f"{place} culture traditions etiquette customs site:.org OR site:.gov OR site:.edu"
        results = fetch_google_search_results(query, api_key, search_engine_id)
        # Filter out any non-web URLs
        filtered_results = [r for r in results if filter_resource_links([r.get('url')])]
        return filtered_results

    def __init__(self):
        self.notes = {}  # simple in-memory store

    def generate_summary(self, culture: str, username: str):
        # default verbosity is 'medium' if not provided by caller
        return generate_culture_summary(culture)

    def generate_summary_with_verbosity(self, culture: str, username: str, verbosity: str = "medium", sections=None):
        return generate_culture_summary(culture, verbosity=verbosity, sections=sections)

    def chat_as_culture(self, culture, persona, message, username):
        return chat_with_persona(culture, persona, message)

    def chat_as_culture_with_verbosity(self, culture, persona, message, username, verbosity: str = "medium"):
        return chat_with_persona(culture, persona, message, verbosity=verbosity)

    def save_note(self, username, culture, user_message, model_output):
        if username not in self.notes:
            self.notes[username] = []

        self.notes[username].append({
            "title": f"{culture} — Chat Note",
            "culture": culture,
            "content": f"User: {user_message}\n\nModel: {model_output}",
            "created_at": now_iso()
        })

    def get_notes(self, username):
        return self.notes.get(username, [])
