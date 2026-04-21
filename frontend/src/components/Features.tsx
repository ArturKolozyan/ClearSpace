"use client";

import { motion } from "framer-motion";
import { Leaf, BadgeCheck, Star } from "lucide-react";

const features = [
  {
    icon: Leaf,
    title: "Эко-средства",
    description: "Используем только безопасные гипоаллергенные средства, безвредные для детей и животных.",
    color: "text-brand-mint",
    bg: "bg-brand-mint/10",
  },
  {
    icon: BadgeCheck,
    title: "Гарантия чистоты",
    description: "Если вас не устроит результат, мы бесплатно переделаем работу в течение 24 часов.",
    color: "text-brand-lavender",
    bg: "bg-brand-lavender/10",
  },
  {
    icon: Star,
    title: "Высокое качество",
    description: "Наши клинеры проходят строгий отбор и регулярное обучение стандартам чистоты.",
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" },
  },
};

export default function Features() {
  return (
    <section id="features" className="py-24 relative scroll-mt-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4"
          >
            Почему выбирают нас
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-lg text-slate-600 text-balance"
          >
            Мы заботимся о вашем комфорте и здоровье, предоставляя сервис премиум-класса по доступной цене.
          </motion.p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid sm:grid-cols-1 md:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="glass-card p-8 group text-center sm:text-left flex flex-col items-center sm:items-start"
            >
              <div
                className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-transform group-hover:scale-110 ${feature.bg} ${feature.color}`}
              >
                <feature.icon size={28} strokeWidth={1.5} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-slate-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}