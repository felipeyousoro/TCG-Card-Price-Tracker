import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import ScrapeCollectionPage from './pages/ScrapeCollection'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/scrape" element={<ScrapeCollectionPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
