import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle, Star } from 'lucide-react';
import { FEATURES } from '../data/features';

export const WhyAttendDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  
  const feature = FEATURES.find(f => f.id === slug);

  if (!feature) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center p-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">Feature not found</h2>
        <button 
          onClick={() => navigate('/')}
          className="text-primary-600 dark:text-primary-400 hover:underline flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <button 
          onClick={() => navigate('/')}
          className="mb-8 flex items-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
        </button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white dark:bg-slate-900 rounded-2xl p-8 md:p-12 shadow-sm border border-slate-200 dark:border-slate-800"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-6">
            {feature.title}
          </h1>
          
          <p className="text-xl text-slate-600 dark:text-slate-400 mb-12 leading-relaxed border-b border-slate-100 dark:border-slate-800 pb-12">
            {feature.details.fullDescription}
          </p>

          <div className="space-y-8">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center">
              <Star className="w-6 h-6 mr-3 text-primary-500" />
              Highlights
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {feature.details.highlights.map((highlight, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800"
                >
                  <CheckCircle className="w-5 h-5 mr-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-700 dark:text-slate-300 font-medium">{highlight}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
