from app import app, scheduled_scrape

if __name__ == '__main__':
    with app.app_context():
        print(scheduled_scrape())
