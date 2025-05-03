class WeatherRecord(db.Model):
    __tablename__ = "weather_records"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    data_type = db.Column(
        db.String(32), nullable=False
    )  # 'current', 'forecast', 'hourly'
    json_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), unique=True, nullable=False)
    temp_unit = db.Column(db.String(8), default="C")  # 'C' or 'F'
    wind_unit = db.Column(db.String(8), default="km/h")  # 'km/h', 'm/s', or 'mph'
    precip_unit = db.Column(db.String(8), default="mm")  # 'mm' or 'inches'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
