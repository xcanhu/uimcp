import { useState, useEffect } from 'react';

export default function DemoSelector({ onDemoSelect, currentDemo }) {
  const [demos, setDemos] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetch('/demos.json')
      .then(res => res.json())
      .then(data => {
        setDemos(data.demos);
        setCategories(data.categories);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load demos:', err);
        setLoading(false);
      });
  }, []);

  const filteredDemos = selectedCategory === 'all' 
    ? demos 
    : demos.filter(demo => demo.category === selectedCategory);



  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading demos...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Choose a Demo</h2>
      
      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedCategory === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => setSelectedCategory('all')}
          >
            All Categories
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              onClick={() => setSelectedCategory(category.id)}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>

      {/* Demo Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDemos.map(demo => (
          <div
            key={demo.id}
            className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border-2 ${
              currentDemo?.id === demo.id ? 'border-blue-500' : 'border-transparent'
            }`}
            onClick={() => onDemoSelect(demo)}
          >
            <div className="aspect-video bg-gray-200 rounded-t-lg overflow-hidden">
              <img
                src={demo.thumbnail}
                alt={demo.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+Cjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOUI5QkEwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPkltYWdlIE5vdCBGb3VuZDwvdGV4dD4KPC9zdmc+';
                }}
              />
            </div>
            <div className="p-4">
              <div className="mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{demo.name}</h3>
              </div>
              <p className="text-gray-600 text-sm mb-3">{demo.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>⏱️ {demo.estimatedTime}</span>
                <span>📋 {demo.steps} steps</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredDemos.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No demos found in this category</div>
        </div>
      )}
    </div>
  );
} 