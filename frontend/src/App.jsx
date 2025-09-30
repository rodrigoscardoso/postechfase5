import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Upload, Video, Download, User, LogOut, Play, CheckCircle, XCircle, Clock } from 'lucide-react'
import './App.css'

const API_BASE = '/api'

function App() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (token) {
      verifyToken()
    }
  }, [token])

  const verifyToken = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
      } else {
        localStorage.removeItem('token')
        setToken(null)
        setUser(null)
      }
    } catch (error) {
      console.error('Token verification failed:', error)
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    }
  }

  const login = async (username, password) => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setToken(data.token)
        setUser(data.user)
        localStorage.setItem('token', data.token)
        setSuccess('Login realizado com sucesso!')
      } else {
        setError(data.error || 'Erro no login')
      }
    } catch (error) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const register = async (username, email, password) => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setToken(data.token)
        setUser(data.user)
        localStorage.setItem('token', data.token)
        setSuccess('Conta criada com sucesso!')
      } else {
        setError(data.error || 'Erro no registro')
      }
    } catch (error) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    setSuccess('Logout realizado com sucesso!')
  }

  if (!user) {
    return <AuthPage onLogin={login} onRegister={register} loading={loading} error={error} success={success} />
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header user={user} onLogout={logout} />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard token={token} />} />
            <Route path="/upload" element={<UploadPage token={token} />} />
            <Route path="/jobs" element={<JobsPage token={token} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

function AuthPage({ onLogin, onRegister, loading, error, success }) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (isLogin) {
      onLogin(formData.username, formData.password)
    } else {
      onRegister(formData.username, formData.email, formData.password)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-blue-600">FIAP X</CardTitle>
          <CardDescription>Sistema de Processamento de Vídeos</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={isLogin ? 'login' : 'register'} onValueChange={(value) => setIsLogin(value === 'login')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Registro</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="username">Usuário</Label>
                  <Input
                    id="username"
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password">Senha</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Entrando...' : 'Entrar'}
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="register">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="username">Usuário</Label>
                  <Input
                    id="username"
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password">Senha</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Criando conta...' : 'Criar conta'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
          
          {error && (
            <Alert className="mt-4 border-red-200 bg-red-50">
              <XCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}
          
          {success && (
            <Alert className="mt-4 border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function Header({ user, onLogout }) {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Video className="h-8 w-8 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">FIAP X Video Processor</h1>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4" />
            <span className="text-sm text-gray-600">{user.username}</span>
          </div>
          <Button variant="outline" size="sm" onClick={onLogout}>
            <LogOut className="h-4 w-4 mr-2" />
            Sair
          </Button>
        </div>
      </div>
    </header>
  )
}

function Dashboard({ token }) {
  const [stats, setStats] = useState(null)
  const [recentJobs, setRecentJobs] = useState([])

  useEffect(() => {
    fetchStats()
    fetchRecentJobs()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/video/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchRecentJobs = async () => {
    try {
      const response = await fetch(`${API_BASE}/video/jobs?per_page=5`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setRecentJobs(data.jobs || [])
      }
    } catch (error) {
      console.error('Error fetching recent jobs:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <div className="space-x-2">
          <Button asChild>
            <a href="/upload">
              <Upload className="h-4 w-4 mr-2" />
              Novo Upload
            </a>
          </Button>
          <Button variant="outline" asChild>
            <a href="/jobs">Ver Todos os Jobs</a>
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total de Jobs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_jobs}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Concluídos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.completed_jobs}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Processando</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.processing_jobs}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Taxa de Sucesso</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.success_rate}%</div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Jobs Recentes</CardTitle>
        </CardHeader>
        <CardContent>
          {recentJobs.length > 0 ? (
            <div className="space-y-3">
              {recentJobs.map((job) => (
                <JobItem key={job.id} job={job} token={token} />
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Nenhum job encontrado</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function UploadPage({ token }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/wmv', 'video/webm']
      if (validTypes.includes(selectedFile.type)) {
        setFile(selectedFile)
        setError('')
      } else {
        setError('Formato de arquivo não suportado. Use: MP4, AVI, MOV, MKV, WMV, WEBM')
        setFile(null)
      }
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError('')
    setSuccess('')

    const formData = new FormData()
    formData.append('video', file)

    try {
      const response = await fetch(`${API_BASE}/video/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess(`Upload realizado com sucesso! Job ID: ${data.job_id}`)
        setFile(null)
        // Reset file input
        document.getElementById('video-upload').value = ''
      } else {
        setError(data.error || 'Erro no upload')
      }
    } catch (error) {
      setError('Erro de conexão')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Upload de Vídeo</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>Selecionar Vídeo</CardTitle>
          <CardDescription>
            Faça upload de um vídeo para extrair frames. Formatos suportados: MP4, AVI, MOV, MKV, WMV, WEBM
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="video-upload">Arquivo de Vídeo</Label>
            <Input
              id="video-upload"
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>
          
          {file && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <strong>Arquivo selecionado:</strong> {file.name}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Tamanho:</strong> {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          )}
          
          <Button 
            onClick={handleUpload} 
            disabled={!file || uploading}
            className="w-full"
          >
            {uploading ? (
              <>
                <Clock className="h-4 w-4 mr-2 animate-spin" />
                Fazendo upload...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Fazer Upload
              </>
            )}
          </Button>
          
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <XCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}
          
          {success && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function JobsPage({ token }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchJobs()
  }, [page])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/video/jobs?page=${page}&per_page=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setJobs(data.jobs || [])
        setTotalPages(data.pages || 1)
      }
    } catch (error) {
      console.error('Error fetching jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Meus Jobs</h2>
        <Button asChild>
          <a href="/upload">
            <Upload className="h-4 w-4 mr-2" />
            Novo Upload
          </a>
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 text-center">
              <Clock className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p>Carregando jobs...</p>
            </div>
          ) : jobs.length > 0 ? (
            <div className="space-y-0">
              {jobs.map((job, index) => (
                <div key={job.id} className={`p-4 ${index !== jobs.length - 1 ? 'border-b' : ''}`}>
                  <JobItem job={job} token={token} />
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <Video className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Nenhum job encontrado</p>
            </div>
          )}
        </CardContent>
      </Card>

      {totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          <Button 
            variant="outline" 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Anterior
          </Button>
          <span className="flex items-center px-4">
            Página {page} de {totalPages}
          </span>
          <Button 
            variant="outline" 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Próxima
          </Button>
        </div>
      )}
    </div>
  )
}

function JobItem({ job, token }) {
  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      processing: { color: 'bg-blue-100 text-blue-800', icon: Play },
      completed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      failed: { color: 'bg-red-100 text-red-800', icon: XCircle }
    }
    
    const config = statusConfig[status] || statusConfig.pending
    const Icon = config.icon
    
    return (
      <Badge className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const handleDownload = async () => {
    try {
      const response = await fetch(`${API_BASE}/video/jobs/${job.id}/download`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `frames_${job.original_filename}_${job.id}.zip`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Download error:', error)
    }
  }

  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-3">
          <h3 className="font-medium text-gray-900">{job.original_filename}</h3>
          {getStatusBadge(job.status)}
        </div>
        <div className="mt-1 text-sm text-gray-500">
          <p>ID: {job.id} • Criado em: {new Date(job.created_at).toLocaleString('pt-BR')}</p>
          {job.frame_count > 0 && <p>{job.frame_count} frames extraídos</p>}
          {job.error_message && <p className="text-red-600">Erro: {job.error_message}</p>}
        </div>
        {job.status === 'processing' && (
          <div className="mt-2">
            <Progress value={job.progress} className="w-full" />
            <p className="text-xs text-gray-500 mt-1">{job.progress}% concluído</p>
          </div>
        )}
      </div>
      
      {job.status === 'completed' && (
        <Button size="sm" onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      )}
    </div>
  )
}

export default App

