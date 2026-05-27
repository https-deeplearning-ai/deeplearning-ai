import { motion } from 'framer-motion';
import { MapPin, Plane, Hotel } from 'lucide-react';

export const TravelAndHotels = () => {
  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true },
    transition: { duration: 0.5 }
  };

  return (
    <div className="py-24 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div {...fadeInUp} className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">Travel & Accommodation</h2>
          <p className="text-slate-600 dark:text-slate-400">Plan your trip to San Francisco.</p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Venue */}
          <motion.div {...fadeInUp} className="bg-white dark:bg-slate-950 p-8 rounded-2xl border border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 rounded-xl bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                <MapPin className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Moscone Center</h3>
                <p className="text-slate-500 dark:text-slate-400">747 Howard St, San Francisco, CA 94103</p>
              </div>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              The Moscone Center is the largest convention and exhibition complex in San Francisco. Located in the heart of the city, it's easily accessible by BART, Muni, and rideshare services.
            </p>
            <div className="aspect-video bg-slate-200 dark:bg-slate-800 rounded-xl flex items-center justify-center mb-6">
              <span className="text-slate-400">Map Placeholder</span>
            </div>
            <div className="flex gap-4">
              <button className="flex-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white py-2 px-4 rounded-lg font-medium transition-colors text-sm flex items-center justify-center gap-2">
                <Plane className="w-4 h-4" /> Flight Deals
              </button>
              <button className="flex-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white py-2 px-4 rounded-lg font-medium transition-colors text-sm flex items-center justify-center gap-2">
                <MapPin className="w-4 h-4" /> Get Directions
              </button>
            </div>
          </motion.div>

          {/* Hotels */}
          <div className="space-y-6">
            {[
              { name: "The Westin St. Francis", dist: "0.4 miles", price: "$289/night", rating: "4.8" },
              { name: "W San Francisco", dist: "0.1 miles", price: "$349/night", rating: "4.7" },
              { name: "San Francisco Marriott Marquis", dist: "0.2 miles", price: "$319/night", rating: "4.6" },
              { name: "InterContinental San Francisco", dist: "0.3 miles", price: "$299/night", rating: "4.8" }
            ].map((hotel, i) => (
              <motion.div 
                key={hotel.name}
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-white dark:bg-slate-950 p-6 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between group hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 group-hover:bg-primary-50 dark:group-hover:bg-primary-900/20 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    <Hotel className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white">{hotel.name}</h4>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{hotel.dist} • {hotel.rating} ★</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-slate-900 dark:text-white">{hotel.price}</p>
                  <span className="text-xs text-primary-600 dark:text-primary-400 font-medium cursor-pointer hover:underline">Book Now</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
