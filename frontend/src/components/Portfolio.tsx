"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const portfolioItems = [
  { id: 1, src: "/portfolio-1.jpg" },
  { id: 2, src: "/portfolio-2.jpg" },
  { id: 3, src: "/portfolio-3.jpg" },
  { id: 4, src: "/portfolio-4.jpg" },
  { id: 5, src: "/portfolio-5.jpg" },
  { id: 6, src: "/portfolio-6.jpg" },
];

export default function Portfolio() {
  return (
    <section id="portfolio" className="py-24 relative scroll-mt-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4"
          >
            Наши работы
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-lg text-slate-600 text-balance"
          >
            Результаты нашей работы говорят сами за себя. Фотографии &quot;До/После&quot;.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {portfolioItems.map((item, index) => (
            <motion.div
              key={`${item.id}-${index}`}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: (index % 3) * 0.1 }}
              className="group relative rounded-[2rem] overflow-hidden aspect-[4/3] shadow-lg shadow-blue-900/5 cursor-pointer"
            >
              <Image
                src={item.src}
                alt="Пример работы"
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-110"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}