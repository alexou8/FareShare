"""
Review Model
Represents peer reviews between users after completed rides.
Supports rating system for trust and quality assurance.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Text, DateTime, ForeignKey, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from src.config.db import Base


class Review(Base):
    """
    Review Model - Peer ratings and feedback between users.
    
    After a ride completes, users can review each other:
    - Passengers can review the driver
    - Driver can review each passenger
    
    Each review includes:
    - Star rating (1-5 stars, required)
    - Written comment (optional)
    - Context (which ride this review is about)
    
    Review Flow Example:
    1. Driver (Alice) posts a ride
    2. Passenger (Bob) books the ride
    3. Ride completes successfully
    4. Bob writes review: "Alice was a great driver! 5 stars"
       - reviewer_id = Bob's ID
       - reviewee_id = Alice's ID
       - ride_id = the completed ride
       - rating = 5
    5. Alice writes review: "Bob was punctual and friendly! 5 stars"
       - reviewer_id = Alice's ID
       - reviewee_id = Bob's ID
       - ride_id = same ride
       - rating = 5
    
    Relationships:
        - ride: The ride where interaction occurred (N:1)
        - reviewer: User writing the review (N:1)
        - reviewee: User being reviewed (N:1)
    """
    __tablename__ = "reviews"
    
    # ===== PRIMARY KEY =====
    # Auto-generated unique ID for each review
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Unique review identifier (UUID)"
    )
    
    # ===== FOREIGN KEYS (LINKS TO OTHER TABLES) =====
    
    # Links to the Ride where this interaction happened
    # Provides context: "This review is about ride #ABC"
    # If ride is deleted, reviews about it are deleted too (CASCADE)
    # Indexed for "show all reviews for ride X" queries
    ride_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rides.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Which ride this review is about"
    )
    
    # Links to the User who wrote this review (the author)
    # If user is deleted, their reviews are deleted too (CASCADE)
    # Indexed for "show all reviews I wrote" queries
    reviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Who wrote this review (author)"
    )
    
    # Links to the User being reviewed (the subject)
    # This user's rating_avg is updated based on these reviews
    # If user is deleted, reviews about them are deleted too (CASCADE)
    # Indexed for "show all reviews about user X" queries
    reviewee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Who is being reviewed (subject)"
    )
    
    # ===== REVIEW CONTENT =====
    
    # Star rating from 1 (worst) to 5 (best)
    # Required field - every review must have a rating
    # Used to calculate user's rating_avg
    # 1 = Very Poor, 2 = Poor, 3 = Average, 4 = Good, 5 = Excellent
    rating = Column(
        Integer,
        nullable=False,
        comment="Star rating: 1 (worst) to 5 (best)"
    )
    
    # Optional written feedback
    # Can be NULL if user only wants to give stars without comment
    # Example: "Great driver, very friendly and safe!"
    comment = Column(
        Text,
        nullable=True,  # Optional field
        comment="Written feedback (optional)"
    )
    
    # ===== TIMESTAMPS =====
    # When this review was posted
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # Auto-set by database
        comment="When review was posted (UTC)"
    )
    
    # ===== DATA VALIDATION RULES =====
    # Database enforces these rules automatically
    
    __table_args__ = (
        # Rating must be 1, 2, 3, 4, or 5 (no other values allowed)
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_rating_range"
        ),
        # ===== PREVENT DUPLICATE REVIEWS =====
        # Same reviewer cannot review same reviewee for same ride twice
        # Example: Bob cannot leave 2 reviews about Alice for the same ride
        # This is a COMPOSITE unique constraint (all 3 fields together must be unique)
        UniqueConstraint(
            "ride_id", "reviewer_id", "reviewee_id",
            name="unique_review_per_ride_pair"
        ),
    )
    
    # ===== RELATIONSHIPS TO OTHER TABLES =====
    
    # The ride this review is about
    # Access via: review.ride.departure_time
    ride = relationship(
        "Ride",
        back_populates="reviews",  # Ride.reviews links back
        lazy="selectin"  # Load ride info automatically
    )
    
    # The user who wrote this review
    # Access via: review.reviewer.full_name
    # Uses foreign_keys because User has TWO relationships to Review
    reviewer = relationship(
        "User",
        foreign_keys=[reviewer_id],  # Specify which column to use
        back_populates="reviews_written",  # User.reviews_written links back
        lazy="selectin"  # Load reviewer info automatically
    )
    
    # The user being reviewed
    # Access via: review.reviewee.rating_avg
    # Uses foreign_keys because User has TWO relationships to Review
    reviewee = relationship(
        "User",
        foreign_keys=[reviewee_id],  # Specify which column to use
        back_populates="reviews_received",  # User.reviews_received links back
        lazy="selectin"  # Load reviewee info automatically
    )
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Review(id={self.id}, reviewer_id={self.reviewer_id}, reviewee_id={self.reviewee_id}, rating={self.rating})>"
