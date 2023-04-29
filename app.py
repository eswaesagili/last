from flask import Flask, render_template, request, redirect, url_for, flash
import cx_Oracle

# create a Flask instance
app = Flask(__name__)
app.secret_key = 'secret_key'

# set up database connection
conn = cx_Oracle.connect('hr/hr@localhost:1521/xe')
print(conn.version)

# create database cursor
cursor = conn.cursor()


# Home page
@app.route('/')
def index():
    return render_template('index.html')


# Movie listing page
@app.route('/movies')
def movies():
    # fetch movies from database
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    return render_template('movies.html', movies=movies)


# Theater listing page
@app.route('/theaters')
def theaters():
    # fetch theaters from database
    cursor.execute("SELECT * FROM theaters")
    app.logger.debug("query executed")
    theaters = cursor.fetchall()
    app.logger.debug("fetch all")
    return render_template('theaters.html', theaters=theaters)


# Ticket booking page
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        # retrieve user inputs from the form
        movie_id = request.form['movie']
        theater_id = request.form['theater']
        num_tickets = request.form['num_tickets']

        # check availability of seats
        cursor.execute("SELECT * FROM theaters WHERE id =:id", {'id': theater_id})
        theater = cursor.fetchone()
        available_seats = theater[2]
        if available_seats < int(num_tickets):
            flash('Sorry, not enough seats available. Please select fewer tickets.')
            return redirect(url_for('booking'))

        # reserve seats and create a booking
        cursor.execute("UPDATE theaters SET CAPACITY=:available_seats WHERE id=:id",
                       {'available_seats': available_seats - int(num_tickets), 'id': theater_id})
        cursor.execute("INSERT INTO ", dict(movie_id=movie_id, theater_id=theater_id, seats_booked=num_tickets,
                                            total_amount=theater[3] * int(num_tickets)))
        conn.commit()

        # display booking details
        cursor.execute("SELECT movies.name, theaters.name, bookings.seats_booked, "
                       "bookings.total_amount FROM movies, theaters, bookings "
                       "WHERE movies.id=:movie_id AND theaters.id=:theater_id AND bookings.movie_id=:movie_id AND \
                        bookings.theater_id=:theater_id", {'movie_id': movie_id, 'theater_id': theater_id})
        booking_details = cursor.fetchone()
        return render_template('booking_confirm.html', booking_details=booking_details)

    else:
        # fetch movies and theaters from database
        cursor.execute("SELECT * FROM movies")
        movies = cursor.fetchall()
        cursor.execute("SELECT * FROM theaters")
        theaters = cursor.fetchall()
        return render_template('booking.html', movies=movies, theaters=theaters)


# Ticket cancellation page
@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if request.method == 'POST':
        # retrieve booking ID from the form
        booking_id = request.form['booking_id']

        # fetch booking details from the database
        cursor.execute("SELECT * FROM bookings WHERE id=:id", {'id': booking_id})
        booking = cursor.fetchone()

        if not booking:
            flash('Invalid booking ID. Please enter a valid ID.')


if __name__ == '__main__':
    app.run(debug=True, port=4400)
