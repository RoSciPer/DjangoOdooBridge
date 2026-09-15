# DjangoOdooBridge
### (to Telegram via Webhook)

A powerful Django-based bridge system that connects Odoo ERP with Telegram Bot API through webhooks, enabling seamless task management and real-time notifications.

## 🌟 Features

- **🔗 Bridge Architecture** - Seamlessly connects Django ↔ Odoo ↔ Telegram
- **📱 Webhook Integration** - Real-time Telegram Bot API communication
- **⚡ Task Management** - Create, assign, and track tasks across systems
- **👥 User Synchronization** - Manage Telegram users through Odoo ERP
- **🎯 API Endpoints** - RESTful API for external integrations
- **📊 Dashboard Interface** - Clean, responsive web interface
- **🔄 Real-time Updates** - Live data synchronization with caching

## 📦 Requirements

- **Python 3.12+** with Django 5.2.7
- **Odoo ERP System** (16.0+ recommended)
- **Odoo Custom Addon**: `telegram_task_manager_2`
- **Telegram Bot** with API token
- **PostgreSQL/SQLite** database

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/RoSciPer/DjangoOdooBridge.git
cd DjangoOdooBridge
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

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST     ┌──────────────────┐    XML-RPC      ┌─────────────────┐
│   Web Browser   │ ◄──────────────► │  Django Bridge   │ ◄─────────────► │   Odoo ERP      │
│   Dashboard     │                  │  (DjangoOdoo     │                 │   + Custom      │
└─────────────────┘                  │   Bridge)        │                 │   Addon         │
                                     └──────────────────┘                 └─────────────────┘
                                                                                    │
                                                                                    │ Webhook
                                                                                    ▼
                                                                          ┌─────────────────┐
                                                                          │  Telegram Bot   │
                                                                          │      API        │
                                                                          └─────────────────┘
                                                                                    │
                                                                                    ▼
                                                                          ┌─────────────────┐
                                                                          │   PostgreSQL    │
                                                                          │   Database      │
                                                                          └─────────────────┘
```

**Key Components:**
- **Django Bridge**: Main API and web interface
- **Odoo Custom Addon**: `/opt/odoo/custom_addons/telegram_task_manager_2/`
- **Telegram Bot**: Webhook configured in Odoo, notifications sent via Odoo
- **Database**: Shared PostgreSQL data layer

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🔗 Links

- **GitHub**: https://github.com/RoSciPer/DjangoOdooBridge

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ **Free to use** - Personal and commercial use
- ✅ **Modify freely** - Adapt to your needs
- ✅ **Distribute** - Share with others
- ✅ **Private use** - Use in closed-source projects
- ⚠️ **No warranty** - Use at your own risk
- 📋 **Attribution required** - Keep copyright notice
