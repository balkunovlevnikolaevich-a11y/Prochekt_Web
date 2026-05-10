from app import create_app, db
from app.models import Advertisement

app = create_app()

# Автоматическое создание рекламы при запуске
with app.app_context():
    if not Advertisement.query.first():
        ad = Advertisement(
            title="Реклама на Prochekt_Web",
            content="Здесь может быть ваша реклама или объявление",
            phone="+79111453106"
        )
        db.session.add(ad)
        db.session.commit()
        print("✅ Реклама автоматически создана!")

if __name__ == '__main__':
    app.run(debug=True)
