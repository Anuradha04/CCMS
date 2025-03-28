import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

from app import app, db
from models import User, Event, Club, ClubMember, Registration


# Helper function to check if user has board member role in a club
def is_board_member(club_id=None):
    if current_user.role == 'dsw':
        return True
    
    if current_user.role != 'board':
        return False
    
    if club_id is None:
        # Check if user is a board member in any club
        board_positions = ['chairperson', 'vice chairperson', 'secretary', 'co-secretary']
        memberships = ClubMember.query.filter(
            ClubMember.user_id == current_user.id,
            ClubMember.position.in_(board_positions)
        ).count()
        return memberships > 0
    
    # Check if user is a board member in the specific club
    board_positions = ['chairperson', 'vice chairperson', 'secretary', 'co-secretary']
    membership = ClubMember.query.filter(
        ClubMember.user_id == current_user.id,
        ClubMember.club_id == club_id,
        ClubMember.position.in_(board_positions)
    ).first()
    
    return membership is not None

# Authentication routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.role == 'board':
            return redirect(url_for('board_dashboard'))
        elif current_user.role == 'dsw':
            return redirect(url_for('dsw_dashboard'))
    return redirect(url_for('login'))

# ch3
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

# ch2
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        # Validate input
        if not all([username, email, password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')
        
        try:
            # Create user
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied. You are not a student.', 'danger')
        return redirect(url_for('index'))
    
    # Get upcoming events
    upcoming_events = Event.query.filter(Event.date_from >= datetime.now().date()).limit(5).all()
    
    # Get clubs/chapters
    clubs = Club.query.filter_by(type='club').limit(5).all()
    chapters = Club.query.filter_by(type='chapter').limit(5).all()
    
    return render_template('student/dashboard.html', 
                          upcoming_events=upcoming_events, 
                          clubs=clubs, 
                          chapters=chapters)

@app.route('/student/events')
@login_required
def student_events():
    if current_user.role != 'student':
        flash('Access denied. You are not a student.', 'danger')
        return redirect(url_for('index'))
    
    # Get filter parameters
    club_id = request.args.get('club_id', type=int)
    date_from = request.args.get('date_from')
    
    # Build query
    query = Event.query
    
    if club_id:
        query = query.filter_by(club_id=club_id)
    
    if date_from:
        try:
            date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Event.date_from >= date_obj)
        except ValueError:
            pass
    
    # Get all events
    events = query.order_by(Event.date_from).all()
    
    # Get all clubs for filter dropdown
    clubs = Club.query.all()
    
    return render_template('student/events.html', events=events, clubs=clubs)

@app.route('/student/clubs')
@login_required
def student_clubs():
    if current_user.role != 'student':
        flash('Access denied. You are not a student.', 'danger')
        return redirect(url_for('index'))
    
    clubs = Club.query.filter_by(type='club').all()
    return render_template('student/clubs.html', clubs=clubs)

@app.route('/student/chapters')
@login_required
def student_chapters():
    if current_user.role != 'student':
        flash('Access denied. You are not a student.', 'danger')
        return redirect(url_for('index'))
    
    chapters = Club.query.filter_by(type='chapter').all()
    return render_template('student/chapters.html', chapters=chapters)

# ch4
@app.route('/student/register/<int:event_id>', methods=['POST'])
@login_required
def register_for_event(event_id):
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Access denied.'}), 403
    
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    registration = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if registration:
        return jsonify({'success': False, 'message': 'Already registered for this event.'}), 400
    
    try:
        # Register for event
        registration = Registration(user_id=current_user.id, event_id=event_id)
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Successfully registered for the event.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred during registration.'}), 500
    
# Board Member routes
@app.route('/board/dashboard')
@login_required
def board_dashboard():
    if current_user.role != 'board':
        flash('Access denied. You are not a board member.', 'danger')
        return redirect(url_for('index'))
    
    # Get clubs where user is a board member
    board_positions = ['chairperson', 'vice chairperson', 'secretary', 'co-secretary']
    memberships = ClubMember.query.filter(
        ClubMember.user_id == current_user.id,
        ClubMember.position.in_(board_positions)
    ).all()
    
    club_ids = [m.club_id for m in memberships]
    clubs = Club.query.filter(Club.id.in_(club_ids)).all()
    
    # Get events from these clubs
    events = Event.query.filter(Event.club_id.in_(club_ids)).order_by(Event.date_from).all()
    
    return render_template('board/dashboard.html', clubs=clubs, events=events)

@app.route('/board/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.role != 'board':
        flash('Access denied. You are not a board member.', 'danger')
        return redirect(url_for('index'))
    
    # Get clubs where user is a board member
    board_positions = ['chairperson', 'vice chairperson', 'secretary', 'co-secretary']
    memberships = ClubMember.query.filter(
        ClubMember.user_id == current_user.id,
        ClubMember.position.in_(board_positions)
    ).all()
    
    club_ids = [m.club_id for m in memberships]
    clubs = Club.query.filter(Club.id.in_(club_ids)).all()
    
    if not clubs:
        flash('You are not a board member of any club/chapter.', 'warning')
        return redirect(url_for('board_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        venue = request.form.get('venue')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        time_from = request.form.get('time_from')
        time_to = request.form.get('time_to')
        poc = request.form.get('poc')
        club_id = request.form.get('club_id', type=int)
        
        # Validate input
        if not all([name, description, venue, date_from, date_to, time_from, time_to, poc, club_id]):
            flash('All fields are required', 'danger')
            return render_template('board/add_event.html', clubs=clubs)
        
        # Check if user is a board member of this club
        if club_id not in club_ids:
            flash('You are not a board member of this club/chapter.', 'danger')
            return render_template('board/add_event.html', clubs=clubs)
        
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            time_from_obj = datetime.strptime(time_from, '%H:%M').time()
            time_to_obj = datetime.strptime(time_to, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return render_template('board/add_event.html', clubs=clubs)
        
        # Create event
        event = Event(
            name=name,
            description=description,
            venue=venue,
            date_from=date_from_obj,
            date_to=date_to_obj,
            time_from=time_from_obj,
            time_to=time_to_obj,
            poc=poc,
            club_id=club_id,
            created_by=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully', 'success')
        return redirect(url_for('board_dashboard'))
    
    return render_template('board/add_event.html', clubs=clubs)

@app.route('/board/modify_event', methods=['GET', 'POST'])
@login_required
def modify_event():
    if current_user.role != 'board':
        flash('Access denied. You are not a board member.', 'danger')
        return redirect(url_for('index'))
    
    # Get clubs where user is a board member
    board_positions = ['chairperson', 'vice chairperson', 'secretary', 'co-secretary']
    memberships = ClubMember.query.filter(
        ClubMember.user_id == current_user.id,
        ClubMember.position.in_(board_positions)
    ).all()
    
    club_ids = [m.club_id for m in memberships]
    
    # Get events from these clubs
    events = Event.query.filter(Event.club_id.in_(club_ids)).order_by(Event.date_from).all()
    
    if not events:
        flash('No events found for your clubs/chapters.', 'warning')
        return redirect(url_for('board_dashboard'))
    
    event_id = request.args.get('event_id', type=int)
    event = None
    
    if event_id:
        event = Event.query.get(event_id)
        if not event or event.club_id not in club_ids:
            flash('Event not found or you do not have permission to modify it.', 'danger')
            return redirect(url_for('modify_event'))
    
    if request.method == 'POST' and event:
        if not validate_csrf(request.form.get('csrf_token')):
            abort(400, description="CSRF token missing or invalid")

        name = request.form.get('name')
        description = request.form.get('description')
        venue = request.form.get('venue')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        time_from = request.form.get('time_from')
        time_to = request.form.get('time_to')
        poc = request.form.get('poc')
        
        # Validate input
        if not all([name, description, venue, date_from, date_to, time_from, time_to, poc]):
            flash('All fields are required', 'danger')
            return render_template('board/modify_event.html', events=events, event=event)
        
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            time_from_obj = datetime.strptime(time_from, '%H:%M').time()
            time_to_obj = datetime.strptime(time_to, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return render_template('board/modify_event.html', events=events, event=event)
        
        # Update event
        event.name = name
        event.description = description
        event.venue = venue
        event.date_from = date_from_obj
        event.date_to = date_to_obj
        event.time_from = time_from_obj
        event.time_to = time_to_obj
        event.poc = poc
        
        db.session.commit()
        
        flash('Event updated successfully', 'success')
        return redirect(url_for('board_dashboard'))
    
    return render_template('board/modify_event.html', events=events, event=event)

@app.route('/board/add_club', methods=['GET', 'POST'])
@login_required
def add_club():
    if current_user.role != 'board':
        flash('Access denied. You are not a board member.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')  # 'club' or 'chapter'
        description = request.form.get('description')
        
        chairperson = request.form.get('chairperson')
        vice_chairperson = request.form.get('vice_chairperson')
        secretary = request.form.get('secretary')
        co_secretary = request.form.get('co_secretary')
        
        # Validate input
        if not all([name, type, description, chairperson]):
            flash('Name, type, description, and chairperson are required', 'danger')
            return render_template('board/add_club.html')
        
        # Create club/chapter
        club = Club(
            name=name,
            type=type,
            description=description
        )
        
        db.session.add(club)
        db.session.flush()  # Get club ID
        
        # Add current user as chairperson if provided username matches
        if chairperson == current_user.username:
            member = ClubMember(
                club_id=club.id,
                user_id=current_user.id,
                position='chairperson'
            )
            db.session.add(member)
        else:
            # Look up user by username
            chair_user = User.query.filter_by(username=chairperson).first()
            if chair_user:
                member = ClubMember(
                    club_id=club.id,
                    user_id=chair_user.id,
                    position='chairperson'
                )
                db.session.add(member)
            else:
                flash(f'User {chairperson} not found. Club created without chairperson.', 'warning')
        
        # Add other positions if provided
        for position, username in [
            ('vice chairperson', vice_chairperson),
            ('secretary', secretary),
            ('co-secretary', co_secretary)
        ]:
            if username:
                user = User.query.filter_by(username=username).first()
                if user:
                    member = ClubMember(
                        club_id=club.id,
                        user_id=user.id,
                        position=position
                    )
                    db.session.add(member)
        
        db.session.commit()
        
        flash(f'{type.capitalize()} created successfully', 'success')
        return redirect(url_for('board_dashboard'))
    
    return render_template('board/add_club.html')

@app.route('/board/modify_club', methods=['GET', 'POST'])
@login_required
def modify_club():
    if current_user.role != 'board':
        flash('Access denied. You are not a board member.', 'danger')
        return redirect(url_for('index'))
    
    # Get clubs where user is a board member
    board_positions = ['chairperson', 'vice chairperson', 'secretary', 'co-secretary']
    memberships = ClubMember.query.filter(
        ClubMember.user_id == current_user.id,
        ClubMember.position.in_(board_positions)
    ).all()
    
    club_ids = [m.club_id for m in memberships]
    clubs = Club.query.filter(Club.id.in_(club_ids)).all()
    
    if not clubs:
        flash('You are not a board member of any club/chapter.', 'warning')
        return redirect(url_for('board_dashboard'))
    
    club_id = request.args.get('club_id', type=int)
    club = None
    club_members = {}
    
    if club_id:
        club = Club.query.get(club_id)
        if not club or club.id not in club_ids:
            flash('Club/Chapter not found or you do not have permission to modify it.', 'danger')
            return redirect(url_for('modify_club'))
        
        # Get current members and their positions
        members = ClubMember.query.filter_by(club_id=club.id).all()
        for member in members:
            user = User.query.get(member.user_id)
            club_members[member.position] = user.username
    
    if request.method == 'POST' and club:
        name = request.form.get('name')
        description = request.form.get('description')
        
        chairperson = request.form.get('chairperson')
        vice_chairperson = request.form.get('vice_chairperson')
        secretary = request.form.get('secretary')
        co_secretary = request.form.get('co_secretary')
        
        # Validate input
        if not all([name, description, chairperson]):
            flash('Name, description, and chairperson are required', 'danger')
            return render_template('board/modify_club.html', 
                                 clubs=clubs, 
                                 club=club, 
                                 members=club_members)
        
        # Update club
        club.name = name
        club.description = description
        
        # Remove all existing members
        ClubMember.query.filter_by(club_id=club.id).delete()
        
        # Add members with new positions
        for position, username in [
            ('chairperson', chairperson),
            ('vice chairperson', vice_chairperson),
            ('secretary', secretary),
            ('co-secretary', co_secretary)
        ]:
            if username:
                user = User.query.filter_by(username=username).first()
                if user:
                    member = ClubMember(
                        club_id=club.id,
                        user_id=user.id,
                        position=position
                    )
                    db.session.add(member)
                else:
                    flash(f'User {username} not found. Position {position} not assigned.', 'warning')
        
        db.session.commit()
        
        flash('Club/Chapter updated successfully', 'success')
        return redirect(url_for('board_dashboard'))
    
    return render_template('board/modify_club.html', 
                         clubs=clubs, 
                         club=club, 
                         members=club_members)

# DSW routes
@app.route('/dsw/dashboard')
@login_required
def dsw_dashboard():
    if current_user.role != 'dsw':
        flash('Access denied. You are not a DSW staff member.', 'danger')
        return redirect(url_for('index'))
    
    # Get event statistics
    upcoming_events = Event.query.filter(Event.date_from >= datetime.now().date()).count()
    past_events = Event.query.filter(Event.date_to < datetime.now().date()).count()
    
    # Get club statistics
    clubs_count = Club.query.filter_by(type='club').count()
    chapters_count = Club.query.filter_by(type='chapter').count()
    
    # Get recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    return render_template('dsw/dashboard.html', 
                          upcoming_events=upcoming_events,
                          past_events=past_events,
                          clubs_count=clubs_count,
                          chapters_count=chapters_count,
                          recent_events=recent_events)

@app.route('/dsw/events')
@login_required
def dsw_events():
    if current_user.role != 'dsw':
        flash('Access denied. You are not a DSW staff member.', 'danger')
        return redirect(url_for('index'))
    
    # Get filter parameters
    club_id = request.args.get('club_id', type=int)
    date_from = request.args.get('date_from')
    
    # Build query
    query = Event.query
    
    if club_id:
        query = query.filter_by(club_id=club_id)
    
    if date_from:
        try:
            date_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Event.date_from >= date_obj)
        except ValueError:
            pass
    
    # Get all events
    events = query.order_by(Event.date_from).all()
    
    # Get all clubs for filter dropdown
    clubs = Club.query.all()
    
    return render_template('dsw/events.html', events=events, clubs=clubs)

@app.route('/dsw/clubs')
@login_required
def dsw_clubs():
    if current_user.role != 'dsw':
        flash('Access denied. You are not a DSW staff member.', 'danger')
        return redirect(url_for('index'))
    
    clubs = Club.query.filter_by(type='club').all()
    
    # Get club member information
    club_members = {}
    for club in clubs:
        members = ClubMember.query.filter_by(club_id=club.id).all()
        club_members[club.id] = []
        for member in members:
            user = User.query.get(member.user_id)
            club_members[club.id].append({
                'username': user.username,
                'position': member.position
            })
    
    return render_template('dsw/clubs.html', clubs=clubs, club_members=club_members)

@app.route('/dsw/chapters')
@login_required
def dsw_chapters():
    if current_user.role != 'dsw':
        flash('Access denied. You are not a DSW staff member.', 'danger')
        return redirect(url_for('index'))
    
    chapters = Club.query.filter_by(type='chapter').all()
    
    # Get chapter member information
    chapter_members = {}
    for chapter in chapters:
        members = ClubMember.query.filter_by(club_id=chapter.id).all()
        chapter_members[chapter.id] = []
        for member in members:
            user = User.query.get(member.user_id)
            chapter_members[chapter.id].append({
                'username': user.username,
                'position': member.position
            })
    
    return render_template('dsw/chapters.html', 
                          chapters=chapters, 
                          chapter_members=chapter_members)

# API routes for AJAX operations
@app.route('/api/event/<int:event_id>')
@login_required
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    return jsonify({
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'venue': event.venue,
        'date_from': event.date_from.strftime('%Y-%m-%d'),
        'date_to': event.date_to.strftime('%Y-%m-%d'),
        'time_from': event.time_from.strftime('%H:%M'),
        'time_to': event.time_to.strftime('%H:%M'),
        'poc': event.poc,
        'club_id': event.club_id
    })
@app.route('/api/event/<int:event_id>', methods=['POST'])
@login_required
def api_event(event_id):
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except:
        abort(400, "Invalid CSRF token")
    return jsonify({'success': True})

@app.route('/api/club/<int:club_id>')
@login_required
def get_club(club_id):
    club = Club.query.get_or_404(club_id)
    
    # Get member information
    members = {}
    for member in ClubMember.query.filter_by(club_id=club.id).all():
        user = User.query.get(member.user_id)
        members[member.position] = user.username
    
    return jsonify({
        'id': club.id,
        'name': club.name,
        'type': club.type,
        'description': club.description,
        'members': members
    })

# ch5
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500