"""
Booking Model
Represents passenger reservations for rides.
Tracks seat reservations, payment, and booking status.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Numeric, DateTime, ForeignKey, CheckConstraint, Index, String
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from src.config.db import Base


class Booking(Base):
    """
    Booking Model - Represents a passenger's reservation for a ride.
    
    When a passenger books a ride, this records:
    - Which ride they're booking
    - How many seats they need
    - How much they paid
    - The booking status (pending → confirmed → completed)
    
    Booking Lifecycle:
    1. "pending" - Just created, waiting for driver confirmation
    2. "confirmed" - Driver accepted, seat(s) reserved
    3. "completed" - Ride finished successfully
    4. "cancelled" - Passenger or driver cancelled
    
    Relationships:
        - ride: The ride being booked (N:1 - many bookings, one ride)
        - passenger: The user making the booking (N:1 - many bookings, one user)
    """
    __tablename__ = "bookings"
    
    # ===== PRIMARY KEY =====
    # Auto-generated unique ID for each booking
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Unique booking identifier (UUID)"
    )
    
    # ===== FOREIGN KEYS (LINKS TO OTHER TABLES) =====
    
    # Links to the Ride being booked
    # If ride is deleted, this booking is deleted too (CASCADE)
    # Indexed for fast "show all bookings for ride X" queries
    ride_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rides.id", ondelete="CASCADE"),  # Link to rides table
        nullable=False,  # Every booking must reference a ride
        index=True,  # Speed up ride lookup
        comment="Which ride is being booked"
    )
    
    # Links to the User who is booking (the passenger)
    # If user is deleted, their bookings are deleted too (CASCADE)
    # Indexed for fast "show all my bookings" queries
    passenger_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),  # Link to users table
        nullable=False,  # Every booking must have a passenger
        index=True,  # Speed up passenger lookup
        comment="Who is booking the ride (passenger)"
    )
    
    # ===== BOOKING DETAILS =====
    
    # How many seats this booking reserves
    # Example: Passenger books for themselves + friend = 2 seats
    # Must be at least 1 (enforced by constraint)
    seats_reserved = Column(
        Integer,
        nullable=False,
        comment="Number of seats reserved (must be >= 1)"
    )
    
    # How much the passenger paid (in USD)
    # Usually: seats_reserved × ride.price_share
    # Example: 2 seats × $15.50 = $31.00
    # Defaults to 0.00 if payment not processed yet
    amount_paid = Column(
        Numeric(6, 2),  # Up to $9999.99
        nullable=False,
        server_default="0.00",  # New bookings start unpaid
        comment="Amount paid in USD (e.g., 31.00 = $31.00)"
    )
    
    # ===== BOOKING STATUS =====
    # Tracks the booking lifecycle
    # "pending" -> waiting for confirmation
    # "confirmed" -> driver accepted, seats locked
    # "cancelled" -> booking was cancelled
    # "completed" -> ride happened successfully
    # Indexed for fast "show all confirmed bookings" queries
    status = Column(
        String(20),
        nullable=False,
        server_default="pending",  # New bookings start as pending
        index=True,  # Speed up status filtering
        comment="Booking state: pending, confirmed, cancelled, or completed"
    )
    
    # ===== TIMESTAMPS =====
    # When this booking was created
    # Indexed for "recent bookings" queries
    booked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # Auto-set by database
        index=True,  # Speed up time-based queries
        comment="When booking was created (UTC)"
    )
    
    # ===== DATA VALIDATION RULES =====
    # Database enforces these rules automatically
    
    __table_args__ = (
        # Must book at least 1 seat (can't book 0 or negative seats)
        CheckConstraint(
            "seats_reserved > 0",
            name="check_seats_reserved_positive"
        ),
        # Amount paid cannot be negative (can be 0 if unpaid/free)
        CheckConstraint(
            "amount_paid >= 0",
            name="check_amount_positive"
        ),
        # Status must be one of these exact values
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled', 'completed')",
            name="check_booking_status"
        ),
    )
    
    # ===== RELATIONSHIPS TO OTHER TABLES =====
    
    # The ride this booking is for
    # Access via: booking.ride.departure_time
    ride = relationship(
        "Ride",
        back_populates="bookings",  # Ride.bookings links back
        lazy="selectin"  # Load ride info automatically
    )
    
    # The passenger who made this booking
    # Access via: booking.passenger.full_name
    passenger = relationship(
        "User",
        back_populates="bookings",  # User.bookings links back
        lazy="selectin"  # Load passenger info automatically
    )
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Booking(id={self.id}, ride_id={self.ride_id}, passenger_id={self.passenger_id}, status='{self.status}')>"
