# Python Docker Dev Example

A demonstration project showcasing Python API development with Docker, created following the [official Docker Python documentation](https://docs.docker.com/language/python/develop/).

##  Features

- **User Registration API**: Register new users with secure password hashing
- **Database Integration**: User data persistence with ID generation
- **Interactive API Documentation**: Auto-generated API docs with Swagger UI
- **Docker Development Environment**: Containerized setup for consistent development

##  API Endpoints

### User Registration
The `/register` endpoint creates new users and returns:
- Hashed password (stored securely)
- Unique user ID from the database

### Documentation
Visit `/docs` to explore:
- Complete API schema
- Interactive endpoint testing
- Request/response examples
- All available routes and data models

##  Getting Started

```bash
# Build and run with Docker
docker-compose up --build

# Access the API documentation
# Navigate to http://localhost:8001/docs
```

## ⚠️ Security Disclaimer

**THIS IS A TEST/DEMONSTRATION PROJECT - NOT PRODUCTION READY**

Known security concerns intentionally not implemented:

- ❌ No rate limiting on endpoints
- ❌ No input validation/sanitization
- ❌ No HTTPS/TLS encryption
- ❌ Sensitive data (hashed passwords) returned in responses
- ❌ No CORS configuration
- ❌ Database credentials in plain text

**Do NOT use this code in production without implementing proper security measures.**

## 🎓 Learning Resources

This project is built for educational purposes following Docker's official Python development guide. Perfect for learning:
- Docker containerization
- Python API development
- Database integration
- API documentation with FastAPI/Swagger

## 📝 License

This is a demonstration project for learning purposes.

---

**Note**: Always implement comprehensive security measures before deploying any application to production environments.
