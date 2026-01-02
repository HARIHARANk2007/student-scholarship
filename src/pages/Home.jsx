import { Link } from 'react-router-dom'

const Home = () => {
  return (
    <>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-float"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-accent-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-float" style={{ animationDelay: '2s' }}></div>
          <div className="absolute bottom-20 left-1/3 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-float" style={{ animationDelay: '4s' }}></div>
        </div>

        <div className="container mx-auto px-4 lg:px-8 py-16 lg:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div data-aos="fade-right">
              <span className="inline-block px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold mb-6">
                🎓 AI-Powered Scholarship Matching
              </span>
              <h1 className="text-4xl lg:text-6xl font-bold text-slate-900 leading-tight mb-6 font-display">
                Find Your Perfect
                <span className="gradient-text"> Scholarship </span>
                Match
              </h1>
              <p className="text-lg lg:text-xl text-slate-600 mb-8 leading-relaxed">
                Upload your marksheet and let our AI instantly match you with scholarships you're eligible for. Simple, fast, and completely free.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/upload" className="btn-primary px-8 py-4 text-lg shadow-xl flex items-center justify-center gap-2 shine">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  Upload Marksheet
                </Link>
                <Link to="/scholarships" className="btn-secondary px-8 py-4 text-lg flex items-center justify-center gap-2">
                  Browse Scholarships
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              </div>

              {/* Stats */}
              <div className="flex gap-8 mt-12">
                <div>
                  <div className="text-3xl font-bold gradient-text">15+</div>
                  <div className="text-slate-500 text-sm">Scholarships</div>
                </div>
                <div>
                  <div className="text-3xl font-bold gradient-text">₹10L+</div>
                  <div className="text-slate-500 text-sm">Total Value</div>
                </div>
                <div>
                  <div className="text-3xl font-bold gradient-text">AI</div>
                  <div className="text-slate-500 text-sm">Powered</div>
                </div>
              </div>
            </div>

            <div data-aos="fade-left" className="relative">
              <div className="relative z-10">
                <div className="bg-white rounded-3xl shadow-2xl p-8 card-hover">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-16 h-16 gradient-bg rounded-2xl flex items-center justify-center">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="font-bold text-lg">Instant Matching</h3>
                      <p className="text-slate-500 text-sm">AI analyzes your profile</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-3 bg-green-50 rounded-xl">
                      <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span className="text-green-700 font-medium">Merit Excellence Scholarship</span>
                      <span className="ml-auto text-green-600 font-bold">92%</span>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-xl">
                      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span className="text-blue-700 font-medium">STEM Excellence Award</span>
                      <span className="ml-auto text-blue-600 font-bold">87%</span>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-xl">
                      <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span className="text-purple-700 font-medium">First Gen Scholar</span>
                      <span className="ml-auto text-purple-600 font-bold">78%</span>
                    </div>
                  </div>
                </div>
              </div>
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-accent-100 rounded-2xl -z-10"></div>
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-primary-100 rounded-2xl -z-10"></div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="text-center mb-16" data-aos="fade-up">
            <span className="inline-block px-4 py-2 bg-accent-100 text-accent-700 rounded-full text-sm font-semibold mb-4">
              Simple Process
            </span>
            <h2 className="text-3xl lg:text-5xl font-bold text-slate-900 font-display">
              How It <span className="gradient-text">Works</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-24 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary-200 via-accent-200 to-primary-200"></div>

            {[
              {
                step: 1,
                title: 'Upload Marksheet',
                description: 'Simply upload your marksheet image or PDF. Our OCR extracts all details automatically.',
                color: 'primary',
                icon: (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                )
              },
              {
                step: 2,
                title: 'AI Analysis',
                description: 'Our AI processes your academic data and compares it with scholarship requirements.',
                color: 'accent',
                icon: (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                )
              },
              {
                step: 3,
                title: 'Get Matched',
                description: 'Receive personalized scholarship recommendations with match scores and deadlines.',
                color: 'primary',
                icon: (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                )
              }
            ].map((item, index) => (
              <div key={item.step} className="relative" data-aos="fade-up" data-aos-delay={index * 200}>
                <div className="bg-white rounded-2xl p-8 shadow-xl card-hover text-center">
                  <div className="w-20 h-20 gradient-bg rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      {item.icon}
                    </svg>
                  </div>
                  <span className={`inline-block px-3 py-1 bg-${item.color}-100 text-${item.color}-700 rounded-full text-sm font-bold mb-4`}>
                    Step {item.step}
                  </span>
                  <h3 className="text-xl font-bold text-slate-900 mb-3">{item.title}</h3>
                  <p className="text-slate-600">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="text-center mb-16" data-aos="fade-up">
            <span className="inline-block px-4 py-2 bg-white/10 text-primary-300 rounded-full text-sm font-semibold mb-4">
              Why Choose Us
            </span>
            <h2 className="text-3xl lg:text-5xl font-bold font-display">
              Powerful <span className="text-primary-400">Features</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: 'AI Matching', desc: 'Smart algorithms find your best fits', icon: '🤖' },
              { title: 'OCR Technology', desc: 'Auto-extract marksheet data', icon: '📄' },
              { title: 'Real-time Updates', desc: 'Latest scholarships daily', icon: '🔄' },
              { title: '100% Free', desc: 'No hidden charges ever', icon: '💎' }
            ].map((feature, index) => (
              <div
                key={feature.title}
                className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300"
                data-aos="fade-up"
                data-aos-delay={index * 100}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="gradient-bg rounded-3xl p-12 text-center text-white relative overflow-hidden" data-aos="fade-up">
            <div className="absolute inset-0 bg-black/10"></div>
            <div className="relative z-10">
              <h2 className="text-3xl lg:text-5xl font-bold mb-6 font-display">
                Ready to Find Your Scholarship?
              </h2>
              <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
                Join thousands of students who have found their perfect scholarship match using our AI-powered platform.
              </p>
              <Link to="/upload" className="inline-flex items-center gap-2 bg-white text-primary-600 px-8 py-4 rounded-xl font-bold text-lg hover:shadow-2xl transition-all hover:scale-105">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Get Started Now
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}

export default Home
