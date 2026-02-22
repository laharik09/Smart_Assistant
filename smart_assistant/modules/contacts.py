"""
modules/contacts.py
====================
Handle contact-related commands:
  • "add contact dad 9876543210"
  • "call dad" / "what's dad's number"
  • "show my contacts"
  • "delete contact dad"
"""

from modules import database as db


def add_contact_handler(user_text: str) -> str:
    """Parse and add a contact from user text."""
    text = user_text.lower()
    
    # Extract name and phone from phrases like:
    # "add contact dad 9876543210"
    # "save contact mom 555-1234"
    # "remember contact john's number is 1234567890"
    
    for trigger in ["add contact", "save contact", "remember contact", "add my contact"]:
        if trigger in text:
            remainder = text.split(trigger, 1)[1].strip()
            break
    else:
        return "Could you say 'add contact' followed by name and number?"
    
    # Simple parsing: split by space/number patterns
    parts = remainder.split()
    if len(parts) < 2:
        return "Please provide both a name and phone number. Example: 'add contact dad 9876543210'"
    
    name = parts[0].capitalize()
    phone = parts[-1]  # Last part should be phone number
    
    # Validate phone (should be mostly digits)
    phone_digits = ''.join(c for c in phone if c.isdigit() or c in '- ()')
    if len(phone_digits) < 7:
        return f"That doesn't look like a valid phone number: {phone}"
    
    db.add_contact(name, phone_digits)
    return f"✓ Saved {name}'s contact: {phone_digits}"


def get_contact_handler(user_text: str) -> str:
    """Get a contact's number from user text."""
    text = user_text.lower()
    
    # Phrases like:
    # "what's dad's number"
    # "call dad"
    # "show me mom's contact"
    
    for trigger in ["what's", "call", "show me", "number", "contact", "phone"]:
        if trigger in text:
            # Extract name (usually the word after trigger or last word)
            parts = text.split()
            # Try to find the contact name (usually last significant word)
            for part in reversed(parts):
                if part not in ["what's", "call", "show", "me", "contact", "number", "phone", "for", "of", "is", "the"]:
                    name = part.rstrip("'s").rstrip("?")
                    break
            break
    else:
        return "Please specify which contact you'd like to call."
    
    contact = db.get_contact(name)
    if not contact:
        return f"I don't have {name} in contacts. Say 'add contact {name} <number>' first."
    
    phone = contact.get("phone")
    if not phone:
        return f"{name}'s contact has no phone number saved."
    
    return f"📞 {name}'s number: {phone}"


def list_contacts_handler() -> str:
    """Show all saved contacts."""
    contacts = db.get_all_contacts()
    
    if not contacts:
        return "You don't have any contacts saved yet. Say 'add contact' to create one."
    
    lines = ["📞 Your Contacts:"]
    for contact in contacts:
        name = contact.get("name", "Unknown")
        phone = contact.get("phone", "")
        email = contact.get("email", "")
        
        info = f"  • {name}"
        if phone:
            info += f": {phone}"
        if email:
            info += f" ({email})"
        
        lines.append(info)
    
    return "\n".join(lines)


def delete_contact_handler(user_text: str) -> str:
    """Delete a contact."""
    text = user_text.lower()
    
    # Phrases like:
    # "delete contact dad"
    # "remove dad from contacts"
    
    for trigger in ["delete", "remove", "remove contact"]:
        if trigger in text:
            remainder = text.split(trigger, 1)[1].strip()
            # Remove common suffixes
            for suffix in [" from contacts", " contact", "contact ", "from contacts"]:
                remainder = remainder.replace(suffix, "").strip()
            name = remainder.capitalize()
            break
    else:
        return "Which contact would you like to delete?"
    
    if not name or name in ["", "Contact"]:
        return "Please specify which contact to delete."
    
    deleted = db.delete_contact(name)
    if deleted:
        return f"✓ Deleted {name} from contacts."
    else:
        return f"I don't have {name} in contacts."


def handle_contact_intent(intent: str, user_text: str) -> str:
    """Route contact-related intents."""
    if intent == "add_contact":
        return add_contact_handler(user_text)
    elif intent == "view_contact":
        return get_contact_handler(user_text)
    elif intent == "list_contacts":
        return list_contacts_handler()
    elif intent == "delete_contact":
        return delete_contact_handler(user_text)
    else:
        return "Contact command not recognized."
