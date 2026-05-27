import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Clock, MapPin, User, Tag } from 'lucide-react';
import type { Session } from '../data/sessions';

interface SessionTileProps {
  session: Session;
}

export const SessionTile = ({ session }: SessionTileProps) => {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.2 }}
      className="group bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm hover:shadow-md transition-all flex flex-col h-full"
    >
      <div className="flex flex-wrap gap-2 items-start mb-4">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryStyles(session.category)} shadow-sm border border-transparent`}>
            'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
          } shadow-sm border border-transparent`}>
          {session.category}
        </span>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
          {session.day}
        </span>
        {session.details?.level && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">
            {session.details.level}
          </span>
        )}
      </div>
      
      <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
        {session.title}
      </h3>
      
      <p className="text-slate-600 dark:text-slate-400 mb-6 line-clamp-2 flex-grow">
        {session.description}
      </p>
      
      <div className="space-y-3 pt-6 border-t border-slate-100 dark:border-slate-800 mt-auto">
        <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
          <User className="h-4 w-4 mr-2 text-slate-400" />
          {session.speaker}
        </div>
        <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
          <Clock className="h-4 w-4 mr-2 text-slate-400" />
          {session.time}
        </div>
        <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
          <MapPin className="h-4 w-4 mr-2 text-slate-400" />
          {session.location}
        </div>
        {session.details?.tracks && session.details.tracks.length > 0 && (
          <div className="flex items-center text-sm text-slate-500 dark:text-slate-500 overflow-hidden text-ellipsis whitespace-nowrap">
            <Tag className="h-4 w-4 mr-2 text-slate-400 flex-shrink-0" />
            <span className="truncate">{session.details.tracks.join(', ')}</span>
          </div>
        )}
      </div>

      <Link 
        to={`/catalog/${session.id}`}
        className="mt-6 inline-flex items-center text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
      >
        View Details <ArrowRight className="ml-1 h-4 w-4" />
      </Link>
    </motion.div>
  );
};
