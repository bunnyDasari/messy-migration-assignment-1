## Major Issues Fixed

1. **SQL Injection** - f-string queries allowed arbitrary SQL execution
2. **Plain Text Passwords** - No password hashing implemented
3. **No Input Validation** - Missing field validation and data sanitization
4. **Global DB Connection** - Thread-unsafe, connection leak risks
5. **Poor Error Handling** - No try-catch blocks, app crashes on errors
6. **Inconsistent Responses** - Mixed string/JSON responses, wrong status codes

## Key Changes Made

### Security
- **Parameterized Queries**: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`
- **Password Hashing**: Added SHA-256 hashing for password storage
- **Input Validation**: Required fields, email format, user ID validation

### Code Quality  
- **Database Management**: `get_db_connection()` function with proper cleanup
- **Error Handling**: Try-catch blocks on all endpoints
- **JSON Responses**: Consistent `jsonify()` usage with proper HTTP status codes
- **Content-Type Validation**: Enforced `application/json` for POST/PUT requests

## Assumptions & Trade-offs

**Assumptions:**
- Existing database schema intact
- Email used for user uniqueness (changed from name)
- Development environment (kept debug=True)

**Trade-offs:**
- Used SHA-256 instead of bcrypt (simpler implementation)
- Basic validation instead of comprehensive library
- SQLite kept instead of PostgreSQL

## Future Improvements

**High Priority:**
- bcrypt password hashing
- JWT authentication
- Connection pooling
- Comprehensive logging

**Nice to Have:**
- Email verification
- Password reset
- Admin dashboard
- Performance monitoring