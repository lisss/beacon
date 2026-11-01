import { Navigate, Route, Routes } from 'react-router-dom'
import { HomePage } from '@/HomePage'
import { TodoPage } from '@/components/TodoPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/learning-list" element={<TodoPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
