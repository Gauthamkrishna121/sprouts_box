# Lush & Healthy (Sprouts Box) - Project Documentation

This is a lightweight, responsive product display website built with Django, Vanilla CSS, and HTML5.

## Project Structure

The project has been separated into backend and frontend directories for better organization:

- **`backend/`**: Contains the Django project (`sproutsbox` settings, the `store` app, database, and configurations).
- **`frontend/`**: Contains the server-rendered HTML templates (`templates/`) and static assets (`static/css`, `static/images`).
- **`venv/`**: The Python virtual environment.

---

## 🚀 How to Run the Website

Follow these steps to start the development server on your machine:

1. **Open PowerShell or Terminal** and navigate to the project folder:
   ```powershell
   cd C:\Users\gauth\OneDrive\Desktop\Sproutsbox
   ```

2. **Start the Django Development Server**:
   ```powershell
   .\venv\Scripts\python.exe backend\manage.py runserver
   ```

3. **View the Website**:
   Open your browser and navigate to: [http://localhost:8000/](http://localhost:8000/)

---

## ⚙️ How to Access the Admin Dashboard

You can use the Django Admin dashboard to easily manage your categories, products, prices, and upload product images.

1. **Go to the Admin URL**:
   Ensure the server is running (Step 2 above), then navigate to: [http://localhost:8000/admin/](http://localhost:8000/admin/)

2. **Login Credentials**:
   A default administrator account has been created for you. 
   - **Username**: `admin`
   - **Password**: `admin123`

*(It is highly recommended that you change this password once you log in or before deploying to production!)*

### Adding Products

1. Click on **Products** under the `STORE` section.
2. Click the **Add product +** button in the top right.
3. Fill in the product details, assign it to a category, and upload an image.
4. Click **Save**. The product will immediately appear on the homepage!
