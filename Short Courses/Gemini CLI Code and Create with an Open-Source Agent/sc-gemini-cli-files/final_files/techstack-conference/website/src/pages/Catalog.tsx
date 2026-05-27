import { useMemo } from 'react';
import { Search, Filter, Calendar, Layers, Mic, Tag } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { useSearchParams } from 'react-router-dom';
import { SESSIONS, type Session } from '../data/sessions';
import { SessionTile } from '../components/SessionTile';

export const Catalog = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Get filter values from URL or default to 'All' or empty string
  const searchQuery = searchParams.get('search') || '';
  const selectedDay = searchParams.get('day') || 'All';
  const selectedCategory = searchParams.get('category') || 'All';
  const selectedSpeaker = searchParams.get('speaker') || 'All';
  const selectedLevel = searchParams.get('level') || 'All';
  const selectedTrack = searchParams.get('track') || 'All';

  // Helper to update a single filter param
  const updateFilter = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value === 'All' || value === '') {
      newParams.delete(key);
    } else {
      newParams.set(key, value);
    }
    setSearchParams(newParams);
  };

  // Static options
  const days = ['All', 'Day 1', 'Day 2', 'Day 3'];
  const categories = ['All', 'Keynote', 'Breakout', 'Customer Story', 'Learning Lab', 'Expo'];
  const levels = ['All', 'Beginner', 'Intermediate', 'Advanced'];

  // Dynamic options derived from data
  const speakers = useMemo(() => {
    const all = SESSIONS.map(s => s.speaker);
    return ['All', ...Array.from(new Set(all)).sort()];
  }, []);

  const tracks = useMemo(() => {
    const all = SESSIONS.flatMap(s => s.details?.tracks || []);
    return ['All', ...Array.from(new Set(all)).sort()];
  }, []);

  const filteredSessions = useMemo<Session[]>(() => {
    return SESSIONS.filter(session => {
      // Search: Check title, description, speaker, fullDescription
      const query = searchQuery.toLowerCase();
      const matchesSearch = 
        session.title.toLowerCase().includes(query) ||
        session.speaker.toLowerCase().includes(query) ||
        session.description.toLowerCase().includes(query) ||
        (session.details?.fullDescription.toLowerCase().includes(query) ?? false);
      
      const matchesDay = selectedDay === 'All' || session.day === selectedDay;
      const matchesCategory = selectedCategory === 'All' || session.category === selectedCategory;
      const matchesSpeaker = selectedSpeaker === 'All' || session.speaker === selectedSpeaker;
      const matchesLevel = selectedLevel === 'All' || session.details?.level === selectedLevel;
      const matchesTrack = selectedTrack === 'All' || (session.details?.tracks.includes(selectedTrack) ?? false);

      return matchesSearch && matchesDay && matchesCategory && matchesSpeaker && matchesLevel && matchesTrack;
    });
  }, [searchQuery, selectedDay, selectedCategory, selectedSpeaker, selectedLevel, selectedTrack]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-10">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">Session Catalog</h1>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            Explore our schedule of events, keynotes, and workshops.
          </p>
        </div>

        {/* Search and Filter Controls */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 mb-8">
          <div className="flex flex-col gap-6">
            
            {/* Row 1: Search */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                placeholder="Search sessions, speakers, or topics..."
                className="block w-full pl-10 pr-3 py-3 border border-slate-200 dark:border-slate-700 rounded-xl leading-5 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition-all"
                value={searchQuery}
                onChange={(e) => updateFilter('search', e.target.value)}
              />
            </div>

            {/* Row 2: Filters Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              
              {/* Day Filter */}
              <div className="relative">
                <label htmlFor="day-filter" className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 ml-1">Day</label>
                <div className="relative">
                  <select
                    id="day-filter"
                    value={selectedDay}
                    onChange={(e) => updateFilter('day', e.target.value)}
                    className="block w-full pl-3 pr-9 py-2.5 text-sm border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none cursor-pointer"
                  >
                    {days.map((day) => (
                      <option key={day} value={day}>{day}</option>
                    ))}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
                    <Calendar className="h-4 w-4" />
                  </div>
                </div>
              </div>

              {/* Category Filter */}
              <div className="relative">
                <label htmlFor="category-filter" className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 ml-1">Category</label>
                <div className="relative">
                  <select
                    id="category-filter"
                    value={selectedCategory}
                    onChange={(e) => updateFilter('category', e.target.value)}
                    className="block w-full pl-3 pr-9 py-2.5 text-sm border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none cursor-pointer"
                  >
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                   <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
                    <Filter className="h-4 w-4" />
                  </div>
                </div>
              </div>

               {/* Level Filter */}
               <div className="relative">
                <label htmlFor="level-filter" className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 ml-1">Level</label>
                <div className="relative">
                  <select
                    id="level-filter"
                    value={selectedLevel}
                    onChange={(e) => updateFilter('level', e.target.value)}
                    className="block w-full pl-3 pr-9 py-2.5 text-sm border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none cursor-pointer"
                  >
                    {levels.map((lvl) => (
                      <option key={lvl} value={lvl}>{lvl}</option>
                    ))}
                  </select>
                   <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
                    <Layers className="h-4 w-4" />
                  </div>
                </div>
              </div>

               {/* Track Filter */}
               <div className="relative">
                <label htmlFor="track-filter" className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 ml-1">Track</label>
                <div className="relative">
                  <select
                    id="track-filter"
                    value={selectedTrack}
                    onChange={(e) => updateFilter('track', e.target.value)}
                    className="block w-full pl-3 pr-9 py-2.5 text-sm border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none cursor-pointer"
                  >
                    {tracks.map((track) => (
                      <option key={track} value={track}>{track}</option>
                    ))}
                  </select>
                   <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
                    <Tag className="h-4 w-4" />
                  </div>
                </div>
              </div>

               {/* Speaker Filter */}
               <div className="relative">
                <label htmlFor="speaker-filter" className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 ml-1">Speaker</label>
                <div className="relative">
                  <select
                    id="speaker-filter"
                    value={selectedSpeaker}
                    onChange={(e) => updateFilter('speaker', e.target.value)}
                    className="block w-full pl-3 pr-9 py-2.5 text-sm border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none cursor-pointer"
                  >
                    {speakers.map((spk) => (
                      <option key={spk} value={spk}>{spk}</option>
                    ))}
                  </select>
                   <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
                    <Mic className="h-4 w-4" />
                  </div>
                </div>
              </div>

            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Showing {filteredSessions.length} sessions
            </p>
            {(searchQuery || selectedDay !== 'All' || selectedCategory !== 'All' || selectedLevel !== 'All' || selectedSpeaker !== 'All' || selectedTrack !== 'All') && (
              <button 
                onClick={() => setSearchParams({})}
                className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
              >
                Clear all filters
              </button>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {filteredSessions.length > 0 ? (
              filteredSessions.map((session) => (
                <SessionTile key={session.id} session={session} />
              ))
            ) : (
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                className="col-span-full text-center py-12"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 mb-4">
                  <Search className="h-8 w-8 text-slate-400" />
                </div>
                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No sessions found</h3>
                <p className="text-slate-500 dark:text-slate-400">
                  Try adjusting your search or filters to find what you're looking for.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};