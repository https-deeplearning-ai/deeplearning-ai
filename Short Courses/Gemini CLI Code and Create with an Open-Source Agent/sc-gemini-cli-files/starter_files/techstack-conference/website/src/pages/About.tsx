import { motion } from 'framer-motion';
import { Brain, Zap, Users, Globe } from 'lucide-react';

export const About = () => {
  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true },
    transition: { duration: 0.5 }
  };

  return (
    <div className="py-24 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div {...fadeInUp}>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6">
              Defining the Next Era of Intelligence
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
              TechStack Conference 2026 isn't just a conference; it's a convergence of the brightest minds in machine learning, deep learning, and generative AI. Whether you're a researcher pushing the boundaries of what's possible or an engineer building the next generation of applications, this is your home.
            </p>
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              We bring together industry leaders from top tech giants, disruptive startups, and academic institutions to share knowledge, debate ethics, and showcase innovations that will shape our future.
            </p>
            <div className="grid grid-cols-2 gap-6">
              {[
                { icon: Brain, text: "Deep Learning Breakthroughs" },
                { icon: Zap, text: "Generative AI Workshops" },
                { icon: Users, text: "Networking Opportunities" },
                { icon: Globe, text: "Global Perspective" }
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400">
                    <item.icon className="w-5 h-5" />
                  </div>
                  <span className="font-medium text-slate-900 dark:text-white">{item.text}</span>
                </div>
              ))}
            </div>
          </motion.div>
          <motion.div 
            {...fadeInUp}
            className="relative"
          >
            <div className="absolute -inset-4 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl opacity-20 blur-2xl"></div>
            <div className="relative aspect-video rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-2xl">
              <div className="absolute inset-0 bg-slate-900/10 dark:bg-slate-900/40 z-10"></div>
               {/* Placeholder for a conference image */}
              <div className="w-full h-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center">
                <span className="text-slate-400 font-medium">Conference Highlights Video Placeholder</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
