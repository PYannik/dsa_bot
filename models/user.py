"""User model for DSA characters."""

class User:
    """Represents a DSA character with their attributes and stats."""

    def __init__(self, id: str, name: str, char_name: str):
        """Initialize a new User instance.

        Args:
            id (str): Discord user ID
            name (str): Discord username
            char_name (str): Character name
        """
        self.id = str(id)  # Ensure ID is always a string
        self.name = name
        self.char_name = char_name
        self.ini = 0
        self.current_ini = 0
        
        # DSA attributes
        self.MU = 0  # Mut
        self.KL = 0  # Klugheit
        self.IN = 0  # Intuition
        self.CH = 0  # Charisma
        self.FF = 0  # Fingerfertigkeit
        self.GE = 0  # Gewandtheit
        self.KO = 0  # Konstitution
        self.KK = 0  # Körperkraft

    def to_string(self) -> str:
        """Convert user data to string format for storage.

        Returns:
            str: User data in CSV format
        """
        return f"{self.id},{self.name},{self.char_name},{self.ini},{self.MU},{self.KL},{self.IN},{self.CH},{self.FF},{self.GE},{self.KO},{self.KK}"

    @classmethod
    def from_string(cls, string: str) -> 'User':
        """Create a User instance from a string.

        Args:
            string (str): User data in CSV format

        Returns:
            User: New User instance or None if data is invalid
        """
        parts = string.strip().split(',')
        if len(parts) >= 12:  # We need at least 12 parts for all attributes
            user = cls(parts[0], parts[1], parts[2])  # ID is now passed as string
            user.ini = int(parts[3])
            user.MU = int(parts[4])
            user.KL = int(parts[5])
            user.IN = int(parts[6])
            user.CH = int(parts[7])
            user.FF = int(parts[8])
            user.GE = int(parts[9])
            user.KO = int(parts[10])
            user.KK = int(parts[11])
            return user
        return None 