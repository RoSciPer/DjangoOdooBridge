# Telegram Task Manager Showcase

# Telegram Task Manager - Demo Version

Django-based demonstration system showcasing task management with Telegram integration and Odoo backend.

## 🌟 Features

- **Real-time Task Management** - Create, assign, and track tasks
- **Telegram Integration** - Instant notifications and bot interaction
- **Odoo Backend** - Professional ERP system integration
- **User Management** - Add and manage Telegram users
- **Dashboard Interface** - Clean, responsive UI with Bootstrap 5
- **Live Demo Access** - Complete working demonstration

## 🚀 Live Demo

Visit the live demo at: **https://django.bidsolana.xyz/dashboard/**

### Full Odoo Access
- **URL**: https://demo.bidsolana.xyz/odoo
- **Username**: `demo@bidsolana.xyz`
- **Password**: `123test`

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telegram-task-manager.git
cd telegram-task-manager
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Odoo connection**
Edit the Odoo connection settings in `showcase/odoo_client.py`:
```python
self.url = "your-odoo-instance.com"
self.db = "your-database"
self.username = "your-username"
self.password = "your-password"
```

5. **Run the development server**
```bash
python manage.py runserver
```

## 📋 API Endpoints

- `POST /api/create-advanced-task/` - Create new tasks
- `POST /api/add-telegram-user/` - Add Telegram users
- `GET /dashboard/` - Main dashboard interface

## 🔧 Technologies Used

- **Backend**: Django 5.2.7, Python 3.12+
- **Frontend**: Bootstrap 5, JavaScript ES6
- **Integration**: Odoo XML-RPC API
- **Database**: SQLite (demo), PostgreSQL (production)
- **Caching**: Django Cache Framework

## 📱 Telegram Bot Setup

To set up your own Telegram bot:

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)
3. Configure the bot token in your Odoo instance
4. Add users through the dashboard interface

## 🎯 Demo Features

- **Task Creation** with priority levels and assignments
- **User Management** with Telegram integration
- **Real-time Updates** with 5-second data refresh
- **Vehicle Assignment** for logistics tasks
- **Report Generation** and tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Live Demo**: https://django.bidsolana.xyz/dashboard/
- **Full Odoo Demo**: https://demo.bidsolana.xyz/odoo
- **GitHub**: https://github.com/yourusername/telegram-task-manager

## 🎯 Purpose

- **Marketing Demo**: Interactive showcase for potential clients
- **Live Testing**: Real Telegram bot integration  
- **Feature Presentation**: Core functionality demonstration
- **Performance**: Fast, lightweight alternative to full Odoo demo

## 🏗️ Structure

```
telegram_showcase_django/
├── manage.py
├── telegram_showcase/     # Django project settings
├── showcase/             # Main app
├── requirements.txt      
└── README.md            
```

## 🚀 Setup

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Database
python manage.py migrate

# Run server
python manage.py runserver 0.0.0.0:8080
```

## 🔗 Related Projects

- **Production System**: `/opt/odoo/custom_addons/telegram_task_manager_2/`
- **Demo URLs**: 
  - Production: `https://odoo.bidsolana.xyz`
  - Demo: `https://demo.bidsolana.xyz` 
  - Showcase: `https://showcase.bidsolana.xyz` (this project)

## 📱 Features

- [ ] Interactive dashboard
- [ ] Telegram bot integration
- [ ] Real-time task updates  
- [ ] Photo report demo
- [ ] Multi-language support
- [ ] Lead generation forms