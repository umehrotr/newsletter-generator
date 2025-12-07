import streamlit as st
import anthropic
import os
from datetime import datetime
import json

# Configuration
st.set_page_config(
    page_title="AI & PM Insights Newsletter",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .article-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .section-header {
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Try Streamlit secrets first (for cloud), fall back to .env (for local)
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")

# Initialize session state
if 'newsletters' not in st.session_state:
    st.session_state.newsletters = []
if 'generated_newsletter' not in st.session_state:
    st.session_state.generated_newsletter = None

# Header
st.markdown("""
<div class="main-header">
    <h1>📰 AI & PM Insights Newsletter</h1>
    <p style="font-size: 1.2rem; margin-top: 0.5rem;">Curated insights for product leaders</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/667eea/ffffff?text=AI+Insights", use_container_width=True)
    
    st.markdown("### ⚙️ Configure Newsletter")
    
    # Date selector
    issue_date = st.date_input(
        "📅 Newsletter Date",
        datetime.now(),
        help="Select the date for this newsletter issue"
    )
    
    st.markdown("---")
    
    # Content settings
    st.markdown("### 📊 Content Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        num_ai = st.number_input("🤖 AI Articles", 1, 3, 2, help="Number of AI insights")
    with col2:
        num_pm = st.number_input("📈 PM Articles", 1, 3, 2, help="Number of PM insights")
    
    st.markdown("---")
    
    # Focus areas
    with st.expander("🎯 AI Focus Areas", expanded=False):
        ai_topics = st.multiselect(
            "Select topics",
            [
                "Generative AI / LLMs",
                "Multilingual AI",
                "AI Product Strategy",
                "AI for E-commerce",
                "AI Ethics & Responsible AI",
                "Emerging AI Capabilities",
                "AI Cost Optimization",
                "Voice AI & Multimodal"
            ],
            default=["Generative AI / LLMs", "Multilingual AI", "AI Product Strategy"],
            label_visibility="collapsed"
        )
    
    with st.expander("📊 PM Focus Areas", expanded=False):
        pm_topics = st.multiselect(
            "Select topics",
            [
                "AI-First Product Management",
                "Product Strategy",
                "Stakeholder Management",
                "Team Leadership",
                "Data-Driven Decision Making",
                "Customer Research",
                "Product Roadmapping",
                "Cross-functional Collaboration"
            ],
            default=["AI-First Product Management", "Product Strategy", "Team Leadership"],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Team context
    team_context = st.text_area(
        "🏢 Team Context",
        placeholder="Optional: Add context about your team (e.g., building multilingual AI for e-commerce)",
        height=100,
        help="Helps tailor content to your specific needs"
    )
    
    st.markdown("---")
    
    # Generate button in sidebar
    generate_button = st.button(
        "🚀 Generate Newsletter",
        type="primary",
        use_container_width=True
    )

# Main content area - Three columns for better layout
if not generate_button and st.session_state.generated_newsletter is None:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 👋 Welcome!")
        st.markdown("""
        Generate curated AI and Product Management insights for your team in seconds.
        
        **What you'll get:**
        - 🤖 Latest AI trends and developments
        - 📊 Timeless PM wisdom and frameworks
        - 📧 Email-ready format
        - 📚 Archived newsletters
        
        **Configure your newsletter in the sidebar and click "Generate Newsletter"**
        """)
        
        st.info("💡 **Tip:** Adjust focus areas and team context for more relevant content")

# Handle newsletter generation
if generate_button:
    with st.spinner("🔍 Researching and curating insights... This takes about 30 seconds."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # AI Insights prompt
            ai_prompt = f"""You are an expert curator of AI insights for product management teams.

Generate {num_ai} high-quality, recent article recommendations for AI insights.

Focus areas: {', '.join(ai_topics)}
Team context: {team_context if team_context else 'Building AI products at scale'}

For each article:
1. **Headline**: Compelling, specific, newsworthy
2. **Source**: Real publication (TechCrunch, The Verge, MIT Tech Review, VentureBeat, etc.)
3. **URL**: Realistic URL format (https://publication.com/2024/12/article-title)
4. **TLDR**: 2-3 sentences explaining the key insight and its significance
5. **Why It Matters**: One clear sentence on relevance to AI product teams

Focus on developments from the last 2-3 months.
Make content highly actionable for AI product managers.

Return ONLY valid JSON array (no markdown, no explanation):
[
  {{
    "headline": "...",
    "source": "...",
    "url": "...",
    "tldr": "...",
    "why_it_matters": "..."
  }}
]"""

            ai_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": ai_prompt}]
            )
            
            ai_text = ai_response.content[0].text
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0].strip()
            ai_articles = json.loads(ai_text)
            
            # PM Insights prompt
            pm_prompt = f"""You are an expert curator of product management insights for senior PMs.

Generate {num_pm} high-quality article recommendations for PM insights.

Focus areas: {', '.join(pm_topics)}

For each article:
1. **Headline**: Compelling, practical, valuable
2. **Source**: Real publication (Lenny's Newsletter, First Round Review, HBR, Product School, etc.)
3. **URL**: Realistic URL format
4. **TLDR**: 2-3 sentences explaining key frameworks/takeaways
5. **Why It Matters**: One sentence on relevance to modern PM practice

These should be TIMELESS insights (6-12 months old is fine).
Focus on practical frameworks and mental models.
Especially valuable for AI-first product management.

Return ONLY valid JSON array (no markdown, no explanation):
[
  {{
    "headline": "...",
    "source": "...",
    "url": "...",
    "tldr": "...",
    "why_it_matters": "..."
  }}
]"""

            pm_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": pm_prompt}]
            )
            
            pm_text = pm_response.content[0].text
            if "```json" in pm_text:
                pm_text = pm_text.split("```json")[1].split("```")[0].strip()
            pm_articles = json.loads(pm_text)
            
            # Create newsletter object
            newsletter = {
                "date": issue_date.strftime("%B %d, %Y"),
                "timestamp": datetime.now().isoformat(),
                "ai_articles": ai_articles,
                "pm_articles": pm_articles,
                "ai_topics": ai_topics,
                "pm_topics": pm_topics
            }
            
            # Save to session state
            st.session_state.newsletters.insert(0, newsletter)
            st.session_state.generated_newsletter = newsletter
            
            st.success("✅ Newsletter generated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating newsletter: {str(e)}")
            st.info("Please check your API key and try again.")

# Display generated newsletter
if st.session_state.generated_newsletter:
    newsletter = st.session_state.generated_newsletter
    
    # Action buttons at top
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        if st.button("📧 View Email Format", use_container_width=True):
            st.session_state.show_email = True
    with col2:
        if st.button("📚 View Archive", use_container_width=True):
            st.session_state.show_archive = True
    with col3:
        if st.button("🔄 Generate New", use_container_width=True):
            st.session_state.generated_newsletter = None
            st.rerun()
    with col4:
        st.download_button(
            "💾",
            json.dumps(newsletter, indent=2),
            f"newsletter_{newsletter['date'].replace(' ', '_').replace(',', '')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Show email format if requested
    if st.session_state.get('show_email', False):
        st.markdown("## 📧 Email Format")
        
        email_content = f"""Subject: Bi-Weekly Insights: AI & Product Management | {newsletter['date']}

Hi team,

Here are this week's curated insights on AI trends and product management excellence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 AI INSIGHTS

"""
        for i, article in enumerate(newsletter['ai_articles'], 1):
            email_content += f"""{i}. {article['headline']}
Source: {article['source']}
Link: {article['url']}

TLDR: {article['tldr']}

Why it matters: {article['why_it_matters']}

"""
        
        email_content += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PRODUCT MANAGEMENT INSIGHTS

"""
        for i, article in enumerate(newsletter['pm_articles'], 1):
            email_content += f"""{i}. {article['headline']}
Source: {article['source']}
Link: {article['url']}

TLDR: {article['tldr']}

Why it matters: {article['why_it_matters']}

"""
        
        email_content += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 SHARE YOUR INSIGHTS

Have insights to share? Reply to this email or post in our team channel.

Happy reading!

Best,
Udit
Head of Product, North America Languages Experience"""
        
        st.text_area(
            "📋 Copy this text into your email:",
            email_content,
            height=500,
            help="Select all (Cmd/Ctrl+A) then copy (Cmd/Ctrl+C)"
        )
        
        st.download_button(
            "💾 Download Email Text",
            email_content,
            f"newsletter_email_{newsletter['date'].replace(' ', '_').replace(',', '')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("⬅️ Back to Preview", use_container_width=True):
            st.session_state.show_email = False
            st.rerun()
    
    # Show archive if requested
    elif st.session_state.get('show_archive', False):
        st.markdown("## 📚 Newsletter Archive")
        st.markdown(f"*{len(st.session_state.newsletters)} newsletters generated*")
        st.markdown("---")
        
        for idx, past_newsletter in enumerate(st.session_state.newsletters):
            with st.expander(
                f"📰 {past_newsletter['date']} | {len(past_newsletter['ai_articles'])} AI + {len(past_newsletter['pm_articles'])} PM articles",
                expanded=(idx == 0)
            ):
                st.markdown(f"*Generated: {datetime.fromisoformat(past_newsletter['timestamp']).strftime('%B %d, %Y at %I:%M %p')}*")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🤖 AI Insights")
                    for i, article in enumerate(past_newsletter['ai_articles'], 1):
                        st.markdown(f"**{i}. [{article['headline']}]({article['url']})**")
                        st.markdown(f"*{article['source']}*")
                        st.caption(article['tldr'])
                        st.markdown("")
                
                with col2:
                    st.markdown("### 📊 PM Insights")
                    for i, article in enumerate(past_newsletter['pm_articles'], 1):
                        st.markdown(f"**{i}. [{article['headline']}]({article['url']})**")
                        st.markdown(f"*{article['source']}*")
                        st.caption(article['tldr'])
                        st.markdown("")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📧 View Email Format", key=f"email_{idx}"):
                        st.session_state.generated_newsletter = past_newsletter
                        st.session_state.show_email = True
                        st.session_state.show_archive = False
                        st.rerun()
                with col_b:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        st.session_state.newsletters.pop(idx)
                        if len(st.session_state.newsletters) == 0:
                            st.session_state.generated_newsletter = None
                            st.session_state.show_archive = False
                        st.rerun()
        
        if st.button("⬅️ Back to Current Newsletter", use_container_width=True):
            st.session_state.show_archive = False
            st.rerun()
    
    # Default: Show newsletter preview
    else:
        # Newsletter header
        st.markdown(f"# 📰 {newsletter['date']}")
        st.markdown("*Curated insights for product leaders*")
        st.markdown("")
        
        # Two-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h2 class="section-header">🤖 AI Insights</h2>', unsafe_allow_html=True)
            st.markdown("*Latest trends and developments in AI*")
            st.markdown("")
            
            for i, article in enumerate(newsletter['ai_articles'], 1):
                st.markdown(f"""
                <div class="article-card">
                    <h3>{i}. <a href="{article['url']}" target="_blank">{article['headline']}</a></h3>
                    <p><em>Source: {article['source']}</em></p>
                    <p><strong>TLDR:</strong> {article['tldr']}</p>
                    <p style="color: #667eea;"><em>💡 Why it matters:</em> {article['why_it_matters']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h2 class="section-header">📊 Product Management Insights</h2>', unsafe_allow_html=True)
            st.markdown("*Timeless wisdom for effective product leadership*")
            st.markdown("")
            
            for i, article in enumerate(newsletter['pm_articles'], 1):
                st.markdown(f"""
                <div class="article-card">
                    <h3>{i}. <a href="{article['url']}" target="_blank">{article['headline']}</a></h3>
                    <p><em>Source: {article['source']}</em></p>
                    <p><strong>TLDR:</strong> {article['tldr']}</p>
                    <p style="color: #667eea;"><em>💡 Why it matters:</em> {article['why_it_matters']}</p>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built with ❤️ using Claude & Streamlit | Created by Udit Mehrotra</p>
    <p style="font-size: 0.9rem;">Part of the AI-First PM Study Plan</p>
</div>
""", unsafe_allow_html=True)