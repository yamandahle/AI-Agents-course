from abc import ABC, abstractmethod
import multiprocessing

class AgentBase(ABC):
    def __init__(self, name, role, expertise, stance):
        self.name = name           # Professional identity
        self.role = role           # Area of expertise
        self.expertise = expertise # Knowledge domain
        self.stance = stance       # Perspective on issues
        self.process = None

    @abstractmethod
    def run(self):
        """Main execution loop for the agent process."""
        pass
