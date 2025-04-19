# 🍽️👀 FoodWatch

A web application that provides real-time access to Montreal's food establishment inspection data. This system allows users to track health violations, submit inspection requests, and receive notifications about food safety incidents across Montreal's restaurants and food establishments.

## 🔍 Key Features
- Search and track health code violations
- Submit inspection requests for establishments
- User profiles with customizable monitoring preferences
- Email notifications for new violations
- Twitter integration for public safety announcements
- Administrative tools for establishment management
- Automated data synchronization with Montreal's open data

Built with Python/Flask, SQLite, and modern web technologies. Perfect for citizens, health inspectors, and restaurant owners who want to stay informed about food safety in Montreal.

## 🚀 How to Execute

1. **Setup Virtual Environment & Install Dependencies**
   ```bash
   make install
   ```

2. **Initialize Database**
   ```bash
   make init-db
   ```

3. **Run Development Server**
   ```bash
   make run
   ```

4. **Run Tests**
   ```bash
   make test
   ```

5. **Code Quality**
   ```bash
   make lint
   ```

6. **Clean Project**
   ```bash
   make clean
   ```

### Prerequisites
- Python 3.x
- pip
- make
