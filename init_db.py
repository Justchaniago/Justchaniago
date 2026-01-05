#!/usr/bin/env python
"""
Initialize database with seed data
Run this to populate the database with sample capabilities
"""

from app import app, db, Service, Portfolio, Experience, Analytics

with app.app_context():
    print("Initializing database...")
    
    # Create all tables
    db.create_all()
    print("✓ Tables created")
    
    # Check and add Services (Capabilities)
    if not Service.query.first():
        print("Adding capabilities...")
        services = [
            Service(
                title="Website Development",
                icon="bi-laptop",
                slug="website-development",
                description="Building fast, responsive, and scalable web applications tailored to your business needs.",
                details="""<h3>Full-Stack Web Development</h3>
                <p>I create modern web applications using Python, Flask, React, and PostgreSQL. From concept to deployment, I handle the entire development lifecycle.</p>
                <h4>What I Offer:</h4>
                <ul>
                    <li><strong>Custom Web Applications</strong> - Tailored solutions for your unique business requirements</li>
                    <li><strong>E-Commerce Platforms</strong> - Complete online stores with payment integration</li>
                    <li><strong>API Development</strong> - RESTful APIs for mobile apps and third-party integrations</li>
                    <li><strong>Database Design</strong> - Efficient and scalable database architecture</li>
                    <li><strong>Cloud Deployment</strong> - Hosting on AWS, Vercel, or your preferred platform</li>
                </ul>
                <h4>Technologies:</h4>
                <p>Python • Flask • JavaScript • React • PostgreSQL • Docker • AWS • Git</p>"""
            ),
            Service(
                title="Branding & Design",
                icon="bi-palette",
                slug="branding-design",
                description="Creating cohesive visual identities that make your brand memorable and professional.",
                details="""<h3>Brand Identity & UI/UX Design</h3>
                <p>I design clean, modern interfaces that prioritize user experience while reflecting your brand's personality.</p>
                <h4>What I Offer:</h4>
                <ul>
                    <li><strong>Logo Design</strong> - Unique and memorable brand marks</li>
                    <li><strong>UI/UX Design</strong> - User-centered interface design</li>
                    <li><strong>Responsive Design</strong> - Mobile-first approach for all devices</li>
                    <li><strong>Design Systems</strong> - Consistent components and style guides</li>
                    <li><strong>Prototyping</strong> - Interactive mockups before development</li>
                </ul>
                <h4>Tools:</h4>
                <p>Figma • Adobe XD • Photoshop • Illustrator</p>"""
            ),
            Service(
                title="Consultation & Strategy",
                icon="bi-clipboard-check",
                slug="consultation-strategy",
                description="Strategic planning and technical consultation to help you make informed decisions about your digital presence.",
                details="""<h3>Technical Consultation & Digital Strategy</h3>
                <p>Not sure where to start? I help businesses understand their technical needs and create actionable roadmaps.</p>
                <h4>What I Offer:</h4>
                <ul>
                    <li><strong>Tech Stack Selection</strong> - Choosing the right tools for your project</li>
                    <li><strong>Project Planning</strong> - Breaking down complex projects into phases</li>
                    <li><strong>Cost Analysis</strong> - Budget-friendly solutions without compromising quality</li>
                    <li><strong>Performance Audit</strong> - Reviewing existing systems for improvements</li>
                    <li><strong>Training & Support</strong> - Ongoing guidance for your team</li>
                </ul>
                <h4>Approach:</h4>
                <p>Practical advice • Cost-effective solutions • Long-term thinking</p>"""
            )
        ]
        db.session.add_all(services)
        db.session.commit()
        print(f"✓ Added {len(services)} capabilities")
    else:
        print("✓ Capabilities already exist")
    
    # Check and add Analytics
    if not Analytics.query.first():
        analytics = Analytics(views=0)
        db.session.add(analytics)
        db.session.commit()
        print("✓ Analytics initialized")
    
    print("\n✅ Database initialization complete!")
    print(f"Total capabilities: {Service.query.count()}")
    print(f"Total portfolios: {Portfolio.query.count()}")
    print(f"Total experiences: {Experience.query.count()}")
