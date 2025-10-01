"""
Constants and utility functions for Nexi assistant.
"""

# Goodbye detection phrases
GOODBYE_PHRASES = [
    "goodbye", "bye", "see you", "exit", "quit", 
    "thank you bye", "good bye", "farewell", 
    "see you later", "talk to you later", "ttyl"
]

# Default response for when no information is found
NO_INFO_RESPONSE = (
    "I don't have information about that. You can try asking another way "
    "or contact the university administration for more details."
)

# Error response for when something goes wrong
ERROR_RESPONSE = "I'm having trouble right now. Could you please try again?"

# Status messages
STATUS_MESSAGES = {
    "pdf_search": "Retrieving information from the knowledge base...",
    "json_search": "Searching calendar and faculty information...",
    "search_complete": "Information search complete.",
    "retrieval_complete": "Information retrieval complete.",
}