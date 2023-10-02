#Django-app backend

##Endpoints for frontend
  1.http://127.0.0.1:8000/api/device/1
  2.http://127.0.0.1:8000/api/device/2
  3."http://127.0.0.1:8000/api/about/"
  4."http://127.0.0.1:8000/api/devices/"
  5."http://127.0.0.1:8000/api/footer/"

##You can create "config.js" file and write ip address there and then import that config file in other files.
Example of setting the base URL in a configuration file (config.js):
```
// config.js
const API_BASE_URL = 'http://localhost:8000/api/'; // Replace with your Django backend API URL
export default API_BASE_URL;

```
