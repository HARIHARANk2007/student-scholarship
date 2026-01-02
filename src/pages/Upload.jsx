import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../context/ToastContext'
import { formatFileSize, api } from '../utils/api'

const Upload = () => {
  const navigate = useNavigate()
  const { showSuccess, showError } = useToast()
  const fileInputRef = useRef(null)

  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)
  const [extractedData, setExtractedData] = useState(null)
  const [matchedScholarships, setMatchedScholarships] = useState(null)
  const [incomeLevel, setIncomeLevel] = useState('< 2 LPA')
  const [region, setRegion] = useState('India')

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      validateAndSetFile(droppedFile)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      validateAndSetFile(selectedFile)
    }
  }

  const validateAndSetFile = (file) => {
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'image/bmp']
    if (!validTypes.includes(file.type)) {
      showError('Invalid file type. Please upload PDF or image files.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      showError('File too large. Maximum size is 10MB.')
      return
    }
    setFile(file)
  }

  const removeFile = () => {
    setFile(null)
    setProgress(0)
    setCurrentStep(0)
    setExtractedData(null)
    setMatchedScholarships(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    setCurrentStep(1)
    setProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const url = '/api/pipeline/complete?income_level=' + encodeURIComponent(incomeLevel) + '&region=' + encodeURIComponent(region)
      
      setCurrentStep(2)
      setProgress(30)

      const response = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 50
            setProgress(percentComplete)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(JSON.parse(xhr.responseText))
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText)
              reject(new Error(errorData.detail || 'Upload failed'))
            } catch {
              reject(new Error('Upload failed'))
            }
          }
        })

        xhr.addEventListener('error', () => reject(new Error('Network error')))
        xhr.open('POST', url)
        xhr.send(formData)
      })

      setProgress(70)
      setCurrentStep(3)

      if (response.success) {
        const profile = response.student_profile || {}
        const recommendations = response.recommendations || []

        const subjects = []
        if (profile.subjects_marks) {
          for (const [name, marks] of Object.entries(profile.subjects_marks)) {
            subjects.push({ name, marks: parseInt(marks) || 0 })
          }
        }

        setExtractedData({
          name: profile.name || 'Unknown',
          percentage: profile.percentage ? profile.percentage + '%' : 'N/A',
          class: profile.class || '',
          board: profile.board || '',
          subjects: subjects.length > 0 ? subjects : [{ name: 'Overall', marks: profile.percentage || 0 }]
        })

        const scholarshipList = recommendations.map((rec, idx) => ({
          id: rec.scholarship?.id || idx + 1,
          title: rec.scholarship?.title || rec.scholarship?.name || 'Scholarship',
          match: Math.round(rec.match_score || 0),
          amount: rec.scholarship?.amount ? 'Rs. ' + rec.scholarship.amount.toLocaleString() : 'Amount varies',
          provider: rec.scholarship?.provider || '',
          explanation: rec.explanation || ''
        }))

        setMatchedScholarships(scholarshipList)
        setProgress(100)
        showSuccess('Marksheet processed successfully!')
      } else {
        showError(response.message || 'Processing failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      showError(error.message || 'Failed to process marksheet. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const steps = [
    { id: 1, label: 'Uploading', icon: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12' },
    { id: 2, label: 'AI Processing', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
    { id: 3, label: 'Matching', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' }
  ]

  const incomeLevels = ['< 2 LPA', '2-5 LPA', '5-8 LPA', '> 8 LPA']
  const regions = ['India', 'Karnataka', 'Tamil Nadu', 'Maharashtra', 'Delhi', 'Other']

  return (
    <section className="relative py-12 overflow-hidden min-h-screen">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-0 w-96 h-96 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-12" data-aos="fade-up">
          <span className="inline-block px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded-full text-sm font-semibold mb-4">
            <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            AI-Powered Extraction
          </span>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 font-display">
            <span className="gradient-text">Upload Your Marksheet</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Our AI extracts your academic details automatically and matches you with the best scholarships
          </p>
        </div>

        <div className="max-w-3xl mx-auto" data-aos="fade-up" data-aos-delay="100">
          <div className="glass-card rounded-2xl p-8 md:p-10 shadow-2xl">
            <form onSubmit={handleSubmit}>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Family Income Level</label>
                  <select
                    value={incomeLevel}
                    onChange={(e) => setIncomeLevel(e.target.value)}
                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer text-gray-700"
                  >
                    {incomeLevels.map((level) => (
                      <option key={level} value={level}>{level}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Region</label>
                  <select
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer text-gray-700"
                  >
                    {regions.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={'relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer group ' + (isDragging ? 'border-purple-500 bg-purple-50/50' : 'border-purple-300 hover:border-purple-500 hover:bg-purple-50/50')}
              >
                <div className="relative mb-6">
                  <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-12 h-12 text-purple-600 animate-bounce-soft" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div className="absolute inset-0 -m-2 rounded-full border-2 border-purple-200 opacity-50 animate-pulse"></div>
                </div>

                <h3 className="text-xl font-semibold text-gray-700 mb-2">Drop your marksheet here</h3>
                <p className="text-gray-500 mb-4">or</p>
                <span className="inline-flex items-center px-8 py-3 btn-primary">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Browse Files
                </span>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
                  onChange={handleFileChange}
                  className="hidden"
                />

                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {['PDF', 'PNG', 'JPG', 'TIFF', 'BMP'].map((format) => (
                    <span key={format} className="px-3 py-1 bg-white/70 rounded-full text-xs text-gray-500 border border-gray-200">
                      {format}
                    </span>
                  ))}
                </div>
              </div>

              {file && (
                <div className="mt-6 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100 animate-slide-up">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-14 h-14 gradient-bg rounded-xl flex items-center justify-center mr-4 shadow-lg">
                        <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-semibold text-gray-800 text-lg">{file.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={removeFile}
                      className="p-2 text-red-500 hover:text-white hover:bg-red-500 rounded-lg transition-all duration-200"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              )}

              {isUploading && (
                <div className="mt-6 animate-slide-up">
                  <div className="flex justify-between mb-6">
                    {steps.map((step, index) => (
                      <div key={step.id} className="flex-1 text-center">
                        <div className={'w-10 h-10 mx-auto rounded-full flex items-center justify-center transition-all duration-300 ' + (currentStep >= step.id ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white' : 'bg-gray-200 text-gray-500')}>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={step.icon} />
                          </svg>
                        </div>
                        <p className="text-xs mt-2 text-gray-500">{step.label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="relative">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        {currentStep === 1 ? 'Uploading file...' : currentStep === 2 ? 'AI Processing...' : 'Finding matches...'}
                      </span>
                      <span className="text-sm font-bold text-purple-600">{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="h-3 rounded-full transition-all duration-300 relative gradient-bg"
                        style={{ width: progress + '%' }}
                      >
                        <div className="absolute inset-0 bg-white/30 animate-pulse"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {!extractedData && (
                <button
                  type="submit"
                  disabled={!file || isUploading}
                  className="w-full mt-8 py-4 btn-primary text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isUploading ? (
                    <>
                      <svg className="animate-spin w-6 h-6" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    <>
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      Analyze & Find Scholarships
                    </>
                  )}
                </button>
              )}
            </form>

            {extractedData && (
              <div className="mt-8 animate-slide-up">
                <div className="border-t border-gray-200 pt-8">
                  <h3 className="text-2xl font-bold text-gray-800 mb-6 font-display">
                    <span className="gradient-text">Extracted Information</span>
                  </h3>

                  <div className="bg-gray-50 rounded-xl p-6 mb-6">
                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Name</p>
                        <p className="font-semibold text-gray-800">{extractedData.name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Overall Percentage</p>
                        <p className="font-semibold text-green-600 text-xl">{extractedData.percentage}</p>
                      </div>
                      {extractedData.class && (
                        <div>
                          <p className="text-sm text-gray-500">Class</p>
                          <p className="font-semibold text-gray-800">{extractedData.class}</p>
                        </div>
                      )}
                      {extractedData.board && (
                        <div>
                          <p className="text-sm text-gray-500">Board</p>
                          <p className="font-semibold text-gray-800">{extractedData.board}</p>
                        </div>
                      )}
                    </div>

                    {extractedData.subjects && extractedData.subjects.length > 0 && (
                      <>
                        <p className="text-sm text-gray-500 mb-2">Subject-wise Marks</p>
                        <div className="space-y-2">
                          {extractedData.subjects.map((subject) => (
                            <div key={subject.name} className="flex items-center justify-between">
                              <span className="text-gray-700">{subject.name}</span>
                              <div className="flex items-center gap-2">
                                <div className="w-32 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="h-2 rounded-full gradient-bg"
                                    style={{ width: Math.min(subject.marks, 100) + '%' }}
                                  ></div>
                                </div>
                                <span className="font-semibold text-gray-800 w-12 text-right">{subject.marks}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>

                  <h3 className="text-2xl font-bold text-gray-800 mb-6 font-display">
                    <span className="gradient-text">Matched Scholarships</span>
                  </h3>

                  {matchedScholarships && matchedScholarships.length > 0 ? (
                    <div className="space-y-4">
                      {matchedScholarships.map((scholarship) => (
                        <div key={scholarship.id} className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-100">
                          <div className="flex items-center gap-4">
                            <div className={'w-12 h-12 rounded-xl flex items-center justify-center font-bold text-white ' + (scholarship.match >= 90 ? 'bg-green-500' : scholarship.match >= 80 ? 'bg-blue-500' : 'bg-purple-500')}>
                              {scholarship.match}%
                            </div>
                            <div>
                              <p className="font-semibold text-gray-800">{scholarship.title}</p>
                              <p className="text-sm text-gray-500">Amount: {scholarship.amount}</p>
                              {scholarship.explanation && (
                                <p className="text-xs text-gray-400 mt-1">{scholarship.explanation}</p>
                              )}
                            </div>
                          </div>
                          <button className="btn-primary px-4 py-2 text-sm">
                            Apply Now
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-xl">
                      <p className="text-gray-500">No matching scholarships found. Try adjusting your income level or region.</p>
                    </div>
                  )}

                  <button
                    onClick={removeFile}
                    className="w-full mt-6 py-3 border-2 border-purple-500 text-purple-600 rounded-xl hover:bg-purple-50 transition-colors font-semibold"
                  >
                    Upload Another Marksheet
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-12">
          {[
            { icon: '', title: 'Secure Upload', desc: 'Your documents are encrypted and secure' },
            { icon: '', title: 'Instant Analysis', desc: 'AI processes your marksheet in seconds' },
            { icon: '', title: 'Smart Matching', desc: 'Get personalized scholarship recommendations' }
          ].map((feature, index) => (
            <div
              key={feature.title}
              className="text-center p-6 glass-card rounded-2xl"
              data-aos="fade-up"
              data-aos-delay={index * 100}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h4 className="font-bold text-gray-800 mb-2">{feature.title}</h4>
              <p className="text-sm text-gray-600">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Upload