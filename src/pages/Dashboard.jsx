import { useState, useEffect } from 'react'

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_students: 1250,
    total_applications: 3420,
    pending: 45,
    approved: 890
  })

  const [applications, setApplications] = useState([
    { id: 1, student: 'Rahul Sharma', scholarship: 'Merit Excellence', date: '2025-12-28', status: 'pending' },
    { id: 2, student: 'Priya Patel', scholarship: 'STEM Award', date: '2025-12-27', status: 'approved' },
    { id: 3, student: 'Amit Kumar', scholarship: 'First Gen Scholar', date: '2025-12-26', status: 'pending' },
    { id: 4, student: 'Sneha Gupta', scholarship: 'Merit Excellence', date: '2025-12-25', status: 'approved' },
    { id: 5, student: 'Vikram Singh', scholarship: 'Sports Excellence', date: '2025-12-24', status: 'rejected' }
  ])

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700'
  }

  return (
    <section className="relative py-8 overflow-hidden min-h-screen">
      {/* Background Decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-gradient-to-br from-purple-400/10 to-pink-400/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-1/4 w-80 h-80 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8" data-aos="fade-up">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2 font-display">
              <span className="gradient-text">Admin Dashboard</span>
            </h1>
            <p className="text-gray-600">Manage applications, track progress, and monitor performance</p>
          </div>
          <div className="mt-4 md:mt-0 flex items-center gap-3">
            <button className="px-4 py-2 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 transition-all flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Export
            </button>
            <button className="btn-primary px-4 py-2 flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Scholarship
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-8">
          {[
            { label: 'Total Students', value: stats.total_students, change: '+12% this month', icon: '👥', gradient: 'from-purple-500 to-pink-500', positive: true },
            { label: 'Applications', value: stats.total_applications, change: '+8% this week', icon: '📄', gradient: 'from-blue-500 to-cyan-500', positive: true },
            { label: 'Pending Review', value: stats.pending, change: 'Needs attention', icon: '⏳', gradient: 'from-yellow-400 to-orange-500', positive: false },
            { label: 'Approved', value: stats.approved, change: 'All verified', icon: '✅', gradient: 'from-green-500 to-emerald-500', positive: true }
          ].map((stat, index) => (
            <div
              key={stat.label}
              className="glass-card rounded-2xl p-6 card-hover"
              data-aos="fade-up"
              data-aos-delay={index * 100}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-500 text-sm mb-1">{stat.label}</p>
                  <p className={`text-3xl font-bold ${stat.label === 'Pending Review' ? 'text-yellow-600' : stat.label === 'Approved' ? 'text-green-600' : 'text-gray-800'}`}>
                    {stat.value.toLocaleString()}
                  </p>
                  <p className={`text-xs mt-2 flex items-center ${stat.positive ? 'text-green-500' : 'text-yellow-500'}`}>
                    {stat.positive && (
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    )}
                    {stat.change}
                  </p>
                </div>
                <div className={`w-14 h-14 bg-gradient-to-br ${stat.gradient} rounded-2xl flex items-center justify-center shadow-lg text-2xl`}>
                  {stat.icon}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Recent Applications Table */}
          <div className="lg:col-span-2 glass-card rounded-2xl overflow-hidden" data-aos="fade-up" data-aos-delay="200">
            <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-800">Recent Applications</h2>
                <p className="text-sm text-gray-500">Review and manage student applications</p>
              </div>
              <a href="#" className="text-sm text-purple-600 hover:text-purple-700 font-medium flex items-center gap-1">
                View All
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Student</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Scholarship</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {applications.map((app) => (
                    <tr key={app.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold">
                            {app.student.charAt(0)}
                          </div>
                          <span className="font-medium text-gray-800">{app.student}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600">{app.scholarship}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-sm">{app.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${statusColors[app.status]}`}>
                          {app.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button className="text-purple-600 hover:text-purple-800 font-medium text-sm">
                          Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="glass-card rounded-2xl p-6" data-aos="fade-up" data-aos-delay="300">
            <h2 className="text-xl font-bold text-gray-800 mb-6">Quick Actions</h2>
            <div className="space-y-4">
              {[
                { label: 'Review Applications', icon: '📋', color: 'purple' },
                { label: 'Add New Scholarship', icon: '➕', color: 'blue' },
                { label: 'Generate Reports', icon: '📊', color: 'green' },
                { label: 'Send Notifications', icon: '🔔', color: 'orange' }
              ].map((action) => (
                <button
                  key={action.label}
                  className="w-full flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-xl transition-all"
                >
                  <span className="text-2xl">{action.icon}</span>
                  <span className="font-medium text-gray-700">{action.label}</span>
                  <svg className="w-5 h-5 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              ))}
            </div>

            {/* Recent Activity */}
            <h3 className="text-lg font-bold text-gray-800 mt-8 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {[
                { text: 'New application from Rahul', time: '2 mins ago' },
                { text: 'Scholarship approved for Priya', time: '1 hour ago' },
                { text: 'New scholarship added', time: '3 hours ago' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-gray-600 flex-1">{activity.text}</span>
                  <span className="text-gray-400">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Dashboard
