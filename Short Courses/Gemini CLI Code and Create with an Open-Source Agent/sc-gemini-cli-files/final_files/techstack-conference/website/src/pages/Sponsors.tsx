import { motion } from 'framer-motion';
import { Check, Mail, Star, Zap, Globe } from 'lucide-react';

export const Sponsors = () => {
  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true },
    transition: { duration: 0.5 }
  };

  return (
    <div className="py-24 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div {...fadeInUp} className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">Become a Sponsor</h2>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Showcase your brand to the world's leading AI experts and decision-makers.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 mb-10">
          {[
            {
              name: "Silver Partner",
              price: "$15,000",
              icon: Star,
              features: ["Logo on website footer", "10 Conference Passes", "Standard Expo Booth (10x10)", "Social Media Mention"]
            },
            {
              name: "Gold Partner",
              price: "$35,000",
              icon: Zap,
              popular: true,
              features: ["Logo on main stage", "25 Conference Passes", "Premium Expo Booth (20x20)", "Breakout Session Slot", "Private Meeting Room"]
            },
            {
              name: "Platinum Partner",
              price: "$75,000",
              icon: Globe,
              features: ["Keynote Mention", "50 Conference Passes", "Island Expo Booth (30x30)", "VIP Dinner Host", "Lead Scanning App Access", "Dedicated Account Manager"]
            }
          ].map((tier, i) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={`relative p-8 rounded-2xl border ${tier.popular ? 'border-primary-500 ring-2 ring-primary-500/20' : 'border-slate-200 dark:border-slate-800'} bg-white dark:bg-slate-900 flex flex-col`}
            >
              {tier.popular && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 px-4 py-1 bg-primary-600 text-white text-sm font-medium rounded-full">
                  Best Value
                </div>
              )}
              <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 mb-6">
                <tier.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{tier.name}</h3>
              <div className="text-2xl font-bold text-slate-900 dark:text-white mb-6">{tier.price}</div>
              <ul className="space-y-4 mb-8 flex-grow">
                {tier.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0" />
                    <span className="text-sm text-slate-700 dark:text-slate-300">{feature}</span>
                  </li>
                ))}
              </ul>
              <a 
                href="mailto:sponsors@aisummit.fake"
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors text-center ${tier.popular ? 'bg-primary-600 hover:bg-primary-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700'}`}
              >
                Contact Us
              </a>
            </motion.div>
          ))}
        </div>

        <div className="bg-slate-50 dark:bg-slate-900 rounded-3xl p-12 text-center">
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">Ready to make an impact?</h3>
          <p className="text-slate-600 dark:text-slate-400 mb-8 max-w-2xl mx-auto">
            Contact our sponsorship team to discuss custom packages and opportunities tailored to your brand goals.
          </p>
          <div className="flex justify-center gap-4">
            <a 
              href="mailto:sponsors@aisummit.fake"
              className="inline-flex items-center justify-center px-8 py-3 text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 transition-colors"
            >
              <Mail className="w-5 h-5 mr-2" />
              Email Sponsorship Team
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
