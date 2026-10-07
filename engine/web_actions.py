"""
JARVIS Web & Media Actions Engine
Handles web searches, YouTube playback, Wikipedia summaries, live weather, and media keys.
"""
import os
import sys
import webbrowser
import urllib.parse
import urllib.request
import json
import datetime
import ctypes
import config

class WebActions:
    def __init__(self):
        pass

    def search_google(self, query: str) -> str:
        """Searches Google for the requested query."""
        if not query or not query.strip():
            return "What would you like me to search for on Google, sir?"
        
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return f"Searching Google for {query}, sir."

    def search_youtube(self, query: str) -> str:
        """Searches YouTube."""
        if not query or not query.strip():
            return "What would you like me to look for on YouTube, sir?"
        
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}, sir."

    def play_youtube(self, query: str) -> str:
        """Finds and plays requested song/video on YouTube."""
        if not query or not query.strip():
            return "What song or video shall I play, sir?"
        
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Playing {query} on YouTube, sir."

    def open_bookmark_or_url(self, target: str) -> str:
        """Opens known bookmarks or web URLs."""
        clean = target.lower().strip()
        for name, url in config.WEB_BOOKMARKS.items():
            if name in clean:
                webbrowser.open(url)
                return f"Opening {name.title()}, sir."

        if not clean.startswith("http"):
            url = f"https://{clean}.com"
        else:
            url = clean

        webbrowser.open(url)
        return f"Opening {target}, sir."

    def get_wikipedia_summary(self, topic: str) -> str:
        """Fetches a concise Wikipedia summary."""
        if not topic or not topic.strip():
            return "Please provide a subject to look up on Wikipedia, sir."

        try:
            encoded = urllib.parse.quote(topic.strip())
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'JarvisAssistant/1.0'})

            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode('utf-8'))
                extract = data.get('extract')
                if extract:
                    # Keep to 2 sentences for pleasant voice response
                    sentences = extract.split('. ')
                    summary = '. '.join(sentences[:2])
                    if not summary.endswith('.'):
                        summary += '.'
                    return f"According to Wikipedia: {summary}"
                else:
                    return f"I couldn't find an exact Wikipedia entry for {topic}, sir."
        except Exception:
            # Fallback to Google Search
            self.search_google(f"who is {topic}")
            return f"I couldn't retrieve the summary directly, so I've opened Google search results for {topic}."

    def get_weather(self, location: str = "") -> str:
        """Fetches live meteorological report from wttr.in."""
        try:
            loc_param = urllib.parse.quote(location.strip()) if location else ""
            url = f"https://wttr.in/{loc_param}?format=j1"
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})

            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                area = data['nearest_area'][0]['areaName'][0]['value']
                curr = data['current_condition'][0]
                temp_c = curr['temp_C']
                desc = curr['weatherDesc'][0]['value']
                humidity = curr['humidity']
                wind_kmph = curr['windspeedKmph']

                return (
                    f"In {area}, it is currently {temp_c} degrees Celsius with {desc}. "
                    f"Humidity is at {humidity} percent and wind speeds are {wind_kmph} kilometers per hour."
                )
        except Exception:
            return "I was unable to establish a telemetry connection to meteorological satellites, sir."

    def get_current_time(self) -> str:
        """Returns spoken time."""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}, sir."

    def get_current_date(self) -> str:
        """Returns spoken date."""
        now = datetime.datetime.now()
        day_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {day_str}, sir."

    def media_control(self, action: str) -> str:
        """Controls global Windows media playback keys."""
        # VK_MEDIA_NEXT_TRACK = 0xB0, VK_MEDIA_PREV_TRACK = 0xB1, VK_MEDIA_PLAY_PAUSE = 0xB3
        VK_MAP = {
            "play": 0xB3,
            "pause": 0xB3,
            "toggle": 0xB3,
            "next": 0xB0,
            "previous": 0xB1,
            "stop": 0xB2
        }

        vk = VK_MAP.get(action.lower().strip())
        if vk:
            try:
                ctypes.windll.user32.keybd_event(vk, 0, 1, 0)
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
                return f"Media {action} executed."
            except Exception as e:
                return f"Media command failed: {e}"
        return "Unknown media command."


# Global singleton instance
web_actions = WebActions()
