import sponsorblock as sb
import logging
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.ERROR)

class SponsorBlockHandler:
    def __init__(self):
        self.client = sb.Client()
        # Categories to skip
        self.categories = [
            "sponsor",
            "selfpromo",
            "interaction",  # Like/Subscribe reminders
            "intro",       # Intros
            "outro",       # Outros
            "preview",     # Preview/Recap
            "filler",      # Filler content
            "music_offtopic"  # Non-music parts
        ]

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL."""
        try:
            parsed = urlparse(url)
            if parsed.hostname == 'youtu.be':
                return parsed.path[1:]
            if parsed.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed.path == '/watch':
                    return parse_qs(parsed.query)['v'][0]
                if parsed.path[:7] == '/embed/':
                    return parsed.path.split('/')[2]
                if parsed.path[:3] == '/v/':
                    return parsed.path.split('/')[2]
        except Exception as e:
            logging.error(f"Error extracting video ID: {e}")
        return None

    async def get_skip_segments(self, url):
        """Get segments to skip for a video."""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return []

            segments = await self.client.get_skip_segments(
                video_id, 
                categories=self.categories
            )
            
            # Sort segments by start time
            segments = sorted(segments, key=lambda x: x.start_time)
            
            return segments

        except Exception as e:
            logging.error(f"Error getting skip segments: {e}")
            return []

    def get_current_segment(self, segments, current_time):
        """Get current segment if we're in one."""
        for segment in segments:
            if segment.start_time <= current_time < segment.end_time:
                return segment
        return None 