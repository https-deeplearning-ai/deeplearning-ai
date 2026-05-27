import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Calendar, Clock, MapPin, Tag, CheckCircle, BookOpen, Shield, Activity } from 'lucide-react';
import { SESSIONS } from '../data/sessions';
import { clsx } from 'clsx';

export const SessionDetail = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const session = SESSIONS.find(s => s.id === sessionId);

  if (!session) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center p-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">Session not found</h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8">The session you are looking for does not exist.</p>
        <button 
          onClick={() => navigate('/catalog')}
          className="text-primary-600 dark:text-primary-400 hover:underline flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Catalog
        </button>
      </div>
    );
  }

  const details = session.details || {
    fullDescription: session.description,
    speakerBio: "Speaker bio coming soon.",
    level: "General Interest",
    tracks: ["General"],
    takeaways: ["Networking", "Knowledge Sharing", "Inspiration"]
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <button 
          onClick={() => navigate(-1)}
          className="mb-8 flex items-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Header */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-800 mb-8">
            <div className="flex flex-wrap gap-3 mb-6">
              <span className={clsx(
                "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border",
                session.category === 'Keynote' && "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-800",
                session.category === 'Breakout' && "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800",
                session.category === 'Learning Lab' && "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-800",
                session.category === 'Customer Story' && "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800",
              )}>
                {session.category}
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700">
                <Activity className="w-3.5 h-3.5 mr-2" />
                {details.level}
              </span>
            </div>

            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6">
              {session.title}
            </h1>

            <div className="grid sm:grid-cols-3 gap-6 text-sm text-slate-600 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 pt-6">
              <div className="flex items-center">
                <Calendar className="w-5 h-5 mr-3 text-primary-500" />
                <div>
                  <span className="block font-semibold text-slate-900 dark:text-white">{session.day}</span>
                  <span>November {session.day === 'Day 1' ? '20' : session.day === 'Day 2' ? '21' : '22'}, 2026</span>
                </div>
              </div>
              <div className="flex items-center">
                <Clock className="w-5 h-5 mr-3 text-primary-500" />
                <div>
                  <span className="block font-semibold text-slate-900 dark:text-white">{session.time}</span>
                  <span>Duration: 1h</span>
                </div>
              </div>
              <div className="flex items-center">
                <MapPin className="w-5 h-5 mr-3 text-primary-500" />
                <div>
                  <span className="block font-semibold text-slate-900 dark:text-white">{session.location}</span>
                  <span>Moscone Center</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="md:col-span-2 space-y-8">
              <section className="bg-white dark:bg-slate-900 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center">
                  <BookOpen className="w-5 h-5 mr-2 text-primary-500" />
                  Abstract
                </h2>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-line">
                  {details.fullDescription}
                </p>
              </section>

              <section className="bg-white dark:bg-slate-900 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-800">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-primary-500" />
                  Key Takeaways
                </h2>
                <ul className="space-y-3">
                  {details.takeaways.map((item, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="w-5 h-5 mr-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-600 dark:text-slate-400">{item}</span>
                    </li>
                  ))}
                </ul>
              </section>
            </div>

            {/* Sidebar */}
            <div className="space-y-8">
              {/* Speaker */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-4">
                  Speaker
                </h3>
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-primary-600 dark:text-primary-400 text-xl font-bold">
                    {session.speaker.charAt(0)}
                  </div>
                  <div>
                    <p className="font-bold text-slate-900 dark:text-white">{session.speaker}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Speaker Title</p>
                  </div>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {details.speakerBio}
                </p>
              </div>

              {/* Tags */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-4">
                  Tracks & Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {details.tracks.map((track) => (
                    <span key={track} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                      <Tag className="w-3 h-3 mr-1" />
                      {track}
                    </span>
                  ))}
                </div>
              </div>

              {/* CTA */}
              <div className="bg-gradient-to-br from-primary-600 to-secondary-600 rounded-2xl p-6 text-white shadow-lg shadow-primary-500/20">
                <h3 className="font-bold mb-2">Save your seat!</h3>
                <p className="text-sm text-primary-100 mb-4">Add this session to your personal schedule.</p>
                <button className="w-full bg-white text-primary-600 font-bold py-2 px-4 rounded-lg text-sm hover:bg-primary-50 transition-colors">
                  Add to Schedule
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
