import requests # type: ignore
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

class WeatherApp:
    def __init__(self):
        self.api_key = "YOUR_API_KEY"  # Replace with a real API key when using
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.history_file = "weather_history.json"
        self.favorites_file = "weather_favorites.json"
        self.history = self.load_data(self.history_file)
        self.favorites = self.load_data(self.favorites_file)
        
    def load_data(self, file_path: str) -> Dict:
        """Load data from file"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {"data": []}
        return {"data": []}
    
    def save_data(self, data: Dict, file_path: str):
        """Save data to file"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    
    def get_weather(self, location: str, units: str = "metric") -> Optional[Dict]:
        """Get current weather for a location"""
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            # For demo purposes, return mock data if API key is not set
            if self.api_key == "YOUR_API_KEY":
                return self.get_mock_weather(location)
                
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Add to history
            self.add_to_history(data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy dữ liệu thời tiết: {e}")
            return None
    
    def get_forecast(self, location: str, units: str = "metric") -> Optional[Dict]:
        """Get 5-day forecast for a location"""
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            # For demo purposes, return mock data if API key is not set
            if self.api_key == "YOUR_API_KEY":
                return self.get_mock_forecast(location)
                
            response = requests.get(self.forecast_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy dữ liệu dự báo: {e}")
            return None
    
    def get_mock_weather(self, location: str) -> Dict:
        """Return mock weather data for demo purposes"""
        current_time = int(time.time())
        
        return {
            "coord": {"lon": 105.85, "lat": 21.03},
            "weather": [
                {
                    "id": 800,
                    "main": "Clear",
                    "description": "trời quang đãng",
                    "icon": "01d"
                }
            ],
            "base": "stations",
            "main": {
                "temp": 30.5,
                "feels_like": 32.8,
                "temp_min": 29.0,
                "temp_max": 31.0,
                "pressure": 1012,
                "humidity": 70
            },
            "visibility": 10000,
            "wind": {
                "speed": 2.5,
                "deg": 120
            },
            "clouds": {
                "all": 5
            },
            "dt": current_time,
            "sys": {
                "type": 1,
                "id": 9308,
                "country": "VN",
                "sunrise": current_time - 21600,  # 6 hours ago
                "sunset": current_time + 21600    # 6 hours from now
            },
            "timezone": 25200,
            "id": 1581130,
            "name": location,
            "cod": 200
        }
    
    def get_mock_forecast(self, location: str) -> Dict:
        """Return mock forecast data for demo purposes"""
        current_time = int(time.time())
        forecast_list = []
        
        # Generate 5 days forecast, 3-hour intervals
        for i in range(0, 40):
            temp = 30 + ((i % 8) - 4)  # Temperature variation through the day
            forecast_list.append({
                "dt": current_time + i * 10800,  # 3 hours intervals
                "main": {
                    "temp": temp,
                    "feels_like": temp + 2,
                    "temp_min": temp - 1,
                    "temp_max": temp + 1,
                    "pressure": 1012,
                    "humidity": 70
                },
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "trời quang đãng",
                        "icon": "01d" if i % 8 < 4 else "01n"
                    }
                ],
                "clouds": {"all": 5},
                "wind": {"speed": 2.5, "deg": 120},
                "visibility": 10000,
                "pop": 0.1,
                "sys": {"pod": "d" if i % 8 < 4 else "n"},
                "dt_txt": datetime.fromtimestamp(current_time + i * 10800).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return {
            "cod": "200",
            "message": 0,
            "cnt": 40,
            "list": forecast_list,
            "city": {
                "id": 1581130,
                "name": location,
                "coord": {"lat": 21.03, "lon": 105.85},
                "country": "VN",
                "population": 1000000,
                "timezone": 25200,
                "sunrise": current_time - 21600,
                "sunset": current_time + 21600
            }
        }
    
    def add_to_history(self, data: Dict):
        """Add weather data to history"""
        # Extract relevant info
        history_entry = {
            "location": data["name"],
            "country": data["sys"]["country"],
            "timestamp": data["dt"],
            "date": datetime.fromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M:%S'),
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
        
        # Add to history
        self.history["data"].append(history_entry)
        
        # Keep only last 10 entries
        if len(self.history["data"]) > 10:
            self.history["data"] = self.history["data"][-10:]
            
        # Save to file
        self.save_data(self.history, self.history_file)
    
    def add_favorite(self, location: str):
        """Add location to favorites"""
        # Check if already in favorites
        for fav in self.favorites["data"]:
            if fav["location"].lower() == location.lower():
                print(f"{location} đã có trong danh sách yêu thích!")
                return
        
        # Add to favorites
        self.favorites["data"].append({
            "location": location,
            "added_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Save to file
        self.save_data(self.favorites, self.favorites_file)
        print(f"Đã thêm {location} vào danh sách yêu thích!")
    
    def remove_favorite(self, index: int) -> bool:
        """Remove location from favorites by index"""
        if 0 <= index < len(self.favorites["data"]):
            removed = self.favorites["data"].pop(index)
            self.save_data(self.favorites, self.favorites_file)
            print(f"Đã xóa {removed['location']} khỏi danh sách yêu thích!")
            return True
        return False
    
    def show_history(self):
        """Display search history"""
        if not self.history["data"]:
            print("Chưa có lịch sử tìm kiếm!")
            return
            
        print("\n=== LỊCH SỬ TÌM KIẾM ===")
        for i, entry in enumerate(reversed(self.history["data"]), 1):
            print(f"{i}. {entry['location']} ({entry['country']}) - {entry['temp']}°C, {entry['description']} - {entry['date']}")
    
    def show_favorites(self):
        """Display favorite locations"""
        if not self.favorites["data"]:
            print("Chưa có địa điểm yêu thích nào!")
            return
            
        print("\n=== ĐỊA ĐIỂM YÊU THÍCH ===")
        for i, fav in enumerate(self.favorites["data"], 1):
            print(f"{i}. {fav['location']} (Thêm vào: {fav['added_on']})")
    
    def format_weather_data(self, data: Dict) -> str:
        """Format weather data for display"""
        if not data:
            return "Không thể lấy dữ liệu thời tiết!"
            
        location = f"{data['name']}, {data['sys']['country']}"
        temp = f"{data['main']['temp']}°C"
        feels_like = f"{data['main']['feels_like']}°C"
        humidity = f"{data['main']['humidity']}%"
        pressure = f"{data['main']['pressure']} hPa"
        wind = f"{data['wind']['speed']} m/s"
        description = data['weather'][0]['description']
        
        # Get weather icon
        icon = data['weather'][0]['icon']
        weather_icon = self.get_weather_icon(icon)
        
        # Format sunrise/sunset times
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        
        # Format current time
        current_time = datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build output
        output = f"\n{'=' * 50}\n"
        output += f"🌍 THỜI TIẾT TẠI {location.upper()} {weather_icon}\n"
        output += f"{'=' * 50}\n"
        output += f"🕒 Cập nhật: {current_time}\n\n"
        output += f"🌡️ Nhiệt độ: {temp} (Cảm giác như: {feels_like})\n"
        output += f"💧 Độ ẩm: {humidity}\n"
        output += f"🔄 Áp suất: {pressure}\n"
        output += f"💨 Gió: {wind}\n"
        output += f"☁️ Thời tiết: {description}\n"
        output += f"🌅 Bình minh: {sunrise}\n"
        output += f"🌇 Hoàng hôn: {sunset}\n"
        
        return output
    
    def format_forecast_data(self, data: Dict) -> str:
        """Format forecast data for display"""
        if not data:
            return "Không thể lấy dữ liệu dự báo!"
            
        location = f"{data['city']['name']}, {data['city']['country']}"
        
        # Build output
        output = f"\n{'=' * 50}\n"
        output += f"🔮 DỰ BÁO 5 NGÀY TẠI {location.upper()}\n"
        output += f"{'=' * 50}\n\n"
        
        # Group forecast by day
        days = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            if date not in days:
                days[date] = []
            days[date].append(item)
        
        # Display forecast for each day
        for date, items in days.items():
            # Get day name
            day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
            day_name_vi = self.translate_day(day_name)
            
            output += f"📅 {day_name_vi} ({date}):\n"
            
            # Calculate min/max temperature for the day
            temps = [item['main']['temp'] for item in items]
            min_temp = min(temps)
            max_temp = max(temps)
            
            output += f"   🌡️ {min_temp}°C - {max_temp}°C\n"
            
            # Display 3-hour intervals
            for item in items:
                time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                temp = item['main']['temp']
                description = item['weather'][0]['description']
                icon = self.get_weather_icon(item['weather'][0]['icon'])
                
                output += f"   ⏰ {time}: {temp}°C, {description} {icon}\n"
            
            output += "\n"
        
        return output
    
    def get_weather_icon(self, icon_code: str) -> str:
        """Get weather emoji based on icon code"""
        icons = {
            "01d": "☀️",  # clear sky day
            "01n": "🌙",  # clear sky night
            "02d": "⛅",  # few clouds day
            "02n": "☁️",  # few clouds night
            "03d": "☁️",  # scattered clouds
            "03n": "☁️",
            "04d": "☁️",  # broken clouds
            "04n": "☁️",
            "09d": "🌧️",  # shower rain
            "09n": "🌧️",
            "10d": "🌦️",  # rain day
            "10n": "🌧️",  # rain night
            "11d": "⛈️",  # thunderstorm
            "11n": "⛈️",
            "13d": "❄️",  # snow
            "13n": "❄️",
            "50d": "🌫️",  # mist
            "50n": "🌫️"
        }
        return icons.get(icon_code, "🌈")
    
    def translate_day(self, day_name: str) -> str:
        """Translate day name to Vietnamese"""
        translations = {
            "Monday": "Thứ Hai",
            "Tuesday": "Thứ Ba",
            "Wednesday": "Thứ Tư",
            "Thursday": "Thứ Năm",
            "Friday": "Thứ Sáu",
            "Saturday": "Thứ Bảy",
            "Sunday": "Chủ Nhật"
        }
        return translations.get(day_name, day_name)
    
    def run_cli(self):
        """Run the weather app CLI"""
        print("\n☁️ ỨNG DỤNG THỜI TIẾT ☀️")
        print("Xem thời tiết hiện tại và dự báo 5 ngày")
        
        while True:
            print("\n" + "=" * 50)
            print("1. Xem thời tiết hiện tại")
            print("2. Xem dự báo 5 ngày")
            print("3. Thêm địa điểm yêu thích")
            print("4. Xem địa điểm yêu thích")
            print("5. Xóa địa điểm yêu thích")
            print("6. Xem lịch sử tìm kiếm")
            print("7. Thoát")
            
            choice = input("\nChọn một tùy chọn (1-7): ")
            
            if choice == "1":
                location = input("Nhập tên thành phố (vd: Hanoi): ")
                data = self.get_weather(location)
                print(self.format_weather_data(data))
                
                # Ask to add to favorites
                add_fav = input("Thêm vào danh sách yêu thích? (y/n): ").lower()
                if add_fav == 'y':
                    self.add_favorite(location)
                    
            elif choice == "2":
                location = input("Nhập tên thành phố (vd: Hanoi): ")
                data = self.get_forecast(location)
                print(self.format_forecast_data(data))
                
            elif choice == "3":
                location = input("Nhập tên thành phố để thêm vào yêu thích: ")
                self.add_favorite(location)
                
            elif choice == "4":
                self.show_favorites()
                
                if self.favorites["data"]:
                    check_weather = input("\nXem thời tiết cho địa điểm yêu thích? Nhập số thứ tự (hoặc 0 để quay lại): ")
                    try:
                        idx = int(check_weather) - 1
                        if 0 <= idx < len(self.favorites["data"]):
                            location = self.favorites["data"][idx]["location"]
                            data = self.get_weather(location)
                            print(self.format_weather_data(data))
                    except ValueError:
                        pass
                    
            elif choice == "5":
                self.show_favorites()
                
                if self.favorites["data"]:
                    remove_idx = input("\nNhập số thứ tự địa điểm muốn xóa (hoặc 0 để quay lại): ")
                    try:
                        idx = int(remove_idx) - 1
                        if idx >= 0:
                            self.remove_favorite(idx)
                    except ValueError:
                        print("Vui lòng nhập một số!")
                    
            elif choice == "6":
                self.show_history()
                
            elif choice == "7":
                print("Cảm ơn bạn đã sử dụng ứng dụng thời tiết!")
                break
                
            else:
                print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    app = WeatherApp()
    app.run_cli()