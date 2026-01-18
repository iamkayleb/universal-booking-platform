import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [services, setServices] = useState([])
  const [myBookings, setMyBookings] = useState([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState(null)
  const [message, setMessage] = useState('')

  // 1. Load Services
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/services/')
      .then(res => {
        console.log("✅ Services Loaded:", res.data)
        setServices(res.data)
      })
      .catch(err => console.error("❌ Services Error:", err))
  }, [])

  // 2. Load Bookings (Runs when token exists)
  useEffect(() => {
    if (token) {
      console.log("🔄 Fetching bookings with token...")
      axios.get('http://127.0.0.1:8000/my-bookings/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => {
        console.log("✅ Bookings Loaded:", res.data)
        setMyBookings(res.data)
      })
      .catch(err => console.error("❌ Bookings Error:", err))
    }
  }, [token])

  const handleLogin = async (e) => {
    e.preventDefault()
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    try {
      const res = await axios.post('http://127.0.0.1:8000/token', formData)
      console.log("✅ Login Success, Token:", res.data.access_token)
      setToken(res.data.access_token)
    } catch (err) {
      console.error("❌ Login Failed:", err)
      setMessage("Login Failed. Check Console.")
    }
  }

  const handleBooking = async (serviceId) => {
    if (!token) return alert("Please log in first!")
    const startTime = prompt("Enter start time (YYYY-MM-DDTHH:MM:SS)", "2026-03-01T10:00:00")
    if (!startTime) return

    try {
      await axios.post('http://127.0.0.1:8000/bookings/', 
        { service_id: serviceId, start_time: startTime },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert("Booking Confirmed!")
      // Refresh list
      const res = await axios.get('http://127.0.0.1:8000/my-bookings/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMyBookings(res.data)
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message))
    }
  }

  // SAFETY FUNCTION: Prevents crashes if data is missing
  const getServiceName = (id) => {
    if (!services || services.length === 0) return `Service #${id} (Loading name...)`
    const service = services.find(s => s.id === id)
    return service ? service.name : `Unknown Service #${id}`
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧘‍♀️ Universal Booking App (Debug Mode)</h1>

      {/* LOGIN */}
      {!token ? (
        <div style={{ background: '#f4f4f4', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
          <h3>Login</h3>
          <form onSubmit={handleLogin} style={{ display: 'flex', gap: '10px' }}>
            <input type="text" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
            <button type="submit">Login</button>
          </form>
          <p style={{color:'red'}}>{message}</p>
        </div>
      ) : (
        <div style={{ background: '#d4edda', padding: '10px', borderRadius: '8px', marginBottom: '20px' }}>
          Logged in as <b>{email}</b>
        </div>
      )}

      <div style={{ display: 'flex', gap: '40px' }}>
        {/* SERVICES */}
        <div style={{ flex: 1 }}>
          <h2>Services</h2>
          {services.map(service => (
            <div key={service.id} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
              <h4>{service.name}</h4>
              <button onClick={() => handleBooking(service.id)}>Book</button>
            </div>
          ))}
        </div>

        {/* BOOKINGS */}
        {token && (
          <div style={{ flex: 1, background: '#fafafa', padding: '15px', border: '1px solid #eee' }}>
            <h2>📅 My Schedule</h2>
            <p>Debug Count: {myBookings.length} bookings found</p>
            
            <ul>
              {myBookings.map(booking => (
                <li key={booking.id} style={{ marginBottom: '10px' }}>
                  <strong>{getServiceName(booking.service_id)}</strong><br/>
                  <small>{booking.start_time}</small>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App