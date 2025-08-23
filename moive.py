import requests
from datetime import datetime
from models import MovieAlert, db
#from models import Movie  # Assuming the Movie model is in yourapp.models

#from yourapp.utils import send_email  # Assuming you have a utility to send emails

def fetch_movie_from_tmdb(movie_name, api_key):
    """Search for the movie on TMDB and return the results."""
    url = f'https://api.themoviedb.org/3/search/movie?api_key={fcaf255fe1e6f7ea86411611fc3b48c4}&query={movie_name}&language=en-US'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error fetching TMDB data for {movie_name}: {response.status_code}")
        return []

def check_movies_in_db(api_key):
    """Check all movies in the database to see if they're available in TMDB."""
    movies_in_db = Movie.query.filter(Movie.alert_sent == False).all()  # Only check movies with alert_sent=False

    for movie in movies_in_db:
        # Fetch the movie from TMDB
        tmdb_movies = fetch_movie_from_tmdb(movie.movie_name, api_key)
        
        if tmdb_movies:  # If movies are found in TMDB
            tmdb_movie = tmdb_movies[0]  # Use the first movie found (you can modify this if needed)

            # Check if the movie is released today or in the past (or however you define "now showing")
            release_date = datetime.strptime(movie.release_date, "%Y-%m-%d").date()
            if release_date <= datetime.today().date():
                # Send email to the user (you can use your preferred method for sending emails)
                send_email(movie.user.email, movie.movie_name)

                # Update the alert_sent flag in the database
                movie.alert_sent = True
                db.session.commit()
                print(f"Alert sent for movie: {movie.movie_name}")

def send_email(to_email, movie_name):
    """Send an email notification about the movie."""
    # Replace with your email sending logic (e.g., SMTP, Flask-Mail, SendGrid, etc.)
    print(f"Sending email to {to_email} about movie: {movie_name}")

if __name__ == "__main__":
    api_key = 'your_tmdb_api_key_here'  # Replace with your actual TMDB API key
    check_movies_in_db(api_key)
