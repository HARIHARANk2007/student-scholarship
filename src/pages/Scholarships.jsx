import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const Scholarships = () => {
  const [scholarships, setScholarships] = useState([
    { id: 1, title: 'Merit Excellence Scholarship', provider: 'National Education Foundation', category: 'Merit-Based', amount: '₹1,00,000', deadline: '2025-03-31', eligibility: '85% and above' },
    { id: 2, title: 'STEM Excellence Award', provider: 'Tech India Foundation', category: 'STEM', amount: '₹75,000', deadline: '2025-02-28', eligibility: '80% in Science/Math' },
    { id: 3, title: 'First Generation Scholar', provider: 'Equal Opportunity Trust', category: 'Need-Based', amount: '₹50,000', deadline: '2025-04-15', eligibility: 'First in family to attend college' },
    { id: 4, title: 'Women in Technology', provider: 'WIT Foundation', category: 'STEM', amount: '₹1,25,000', deadline: '2025-03-15', eligibility: 'Female students in tech' },
    { id: 5, title: 'Sports Excellence Award', provider: 'Sports Authority', category: 'Sports', amount: '₹60,000', deadline: '2025-05-01', eligibility: 'State-level sports achievement' },
    { id: 6, title: 'Rural Development Scholarship', provider: 'Ministry of Education', category: 'Need-Based', amount: '₹40,000', deadline: '2025-04-30', eligibility: 'Rural background students' }
  ])

  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [sortBy, setSortBy] = useState('relevance')

  const categories = ['Merit-Based', 'Need-Based', 'STEM', 'Sports', 'Arts']

  const filteredScholarships = scholarships.filter((s) => {
    const matchesSearch = s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          s.provider.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = !selectedCategory || s.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const gradients = [
    'from-purple-500 via-pink-500 to-blue-500',
    'from-blue-500 via-cyan-500 to-teal-500',
    'from-orange-500 via-pink-500 to-purple-500',
    'from-green-500 via-teal-500 to-blue-500',
    'from-red-500 via-orange-500 to-yellow-500',
    'from-indigo-500 via-purple-500 to-pink-500'
  ]

  return (
    <section className="relative py-12 overflow-hidden min-h-screen">
      {/* Background Decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Page Header */}
        <div className="text-center mb-12" data-aos="fade-up">
          <span className="inline-block px-4 py-2 bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-700 rounded-full text-sm font-semibold mb-4">
            <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            {scholarships.length}+ Opportunities
          </span>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 font-display">
            <span className="gradient-text">Browse Scholarships</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover scholarship opportunities tailored to your academic profile and goals
          </p>
        </div>

        {/* Stats Row */}
        <div className="flex flex-wrap justify-center gap-8 mb-12" data-aos="fade-up" data-aos-delay="100">
          <div className="text-center">
            <div className="text-3xl font-bold gradient-text">₹50L+</div>
            <div className="text-sm text-gray-500">Total Value</div>
          </div>
          <div className="w-px h-12 bg-gray-200 hidden md:block"></div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">100+</div>
            <div className="text-sm text-gray-500">Active Scholarships</div>
          </div>
          <div className="w-px h-12 bg-gray-200 hidden md:block"></div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">50+</div>
            <div className="text-sm text-gray-500">Partners</div>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="glass-card rounded-2xl p-6 md:p-8 mb-10 shadow-xl max-w-5xl mx-auto" data-aos="fade-up" data-aos-delay="200">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search by name, provider, or keyword..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all text-gray-700"
              />
            </div>

            {/* Category Filter */}
            <div className="md:w-64">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-4 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer text-gray-700"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-6 max-w-6xl mx-auto" data-aos="fade-up" data-aos-delay="300">
          <p className="text-gray-600">
            Showing <span className="font-semibold text-gray-800">{filteredScholarships.length}</span> scholarships
          </p>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 cursor-pointer"
            >
              <option value="relevance">Relevance</option>
              <option value="deadline">Deadline</option>
              <option value="amount">Amount</option>
            </select>
          </div>
        </div>

        {/* Scholarships Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {filteredScholarships.map((scholarship, index) => (
            <div
              key={scholarship.id}
              className="glass-card rounded-2xl overflow-hidden card-hover group"
              data-aos="fade-up"
              data-aos-delay={index * 50}
            >
              {/* Card Header with Gradient */}
              <div className={`relative h-32 bg-gradient-to-br ${gradients[index % gradients.length]} p-6`}>
                <div className="absolute inset-0 bg-black/10"></div>
                <div className="relative z-10">
                  <span className="inline-block bg-white/20 backdrop-blur-sm text-white px-3 py-1 rounded-full text-xs font-semibold">
                    {scholarship.category}
                  </span>
                </div>
                {/* Provider Logo Placeholder */}
                <div className="absolute -bottom-6 right-6 w-14 h-14 bg-white rounded-xl shadow-lg flex items-center justify-center">
                  <span className="text-xl font-bold gradient-text">
                    {scholarship.provider.substring(0, 2).toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="p-6 pt-4">
                <h3 className="font-bold text-lg text-gray-800 mb-1 group-hover:text-purple-600 transition-colors line-clamp-2">
                  {scholarship.title}
                </h3>
                <p className="text-gray-500 text-sm mb-4">{scholarship.provider}</p>

                {/* Info Row */}
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100">
                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wide">Amount</p>
                    <p className="font-bold text-lg gradient-text">{scholarship.amount}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400 uppercase tracking-wide">Deadline</p>
                    <p className="font-semibold text-gray-700">{scholarship.deadline}</p>
                  </div>
                </div>

                {/* Eligibility */}
                <div className="mb-4">
                  <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Eligibility</p>
                  <p className="text-sm text-gray-600">{scholarship.eligibility}</p>
                </div>

                {/* Action Button */}
                <Link
                  to="/upload"
                  className="w-full btn-primary py-3 flex items-center justify-center gap-2"
                >
                  Apply Now
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredScholarships.length === 0 && (
          <div className="text-center py-12" data-aos="fade-up">
            <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">No scholarships found</h3>
            <p className="text-gray-600">Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>
    </section>
  )
}

export default Scholarships
