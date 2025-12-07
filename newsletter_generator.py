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

# Custom CSS
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
    .search-tip {
        background-color: #e8f4f8;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #1a5f7a;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# API key setup
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
    st.markdown("### ⚙️ Configure Newsletter")
    
    issue_date = st.date_input(
        "📅 Newsletter Date",
        datetime.now(),
        help="Select the date for this newsletter issue"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Content Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        num_ai = st.number_input("🤖 AI Insights", 1, 3, 2, help="Number of AI insights")
    with col2:
        num_pm = st.number_input("📈 PM Insights", 1, 3, 2, help="Number of PM insights")
    
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
    
    team_context = st.text_area(
        "🏢 Team Context",
        placeholder="Optional: Add context about your team",
        height=100,
        help="Helps tailor content to your specific needs"
    )
    
    st.markdown("---")
    
    generate_button = st.button(
        "🚀 Generate Newsletter",
        type="primary",
        use_container_width=True
    )

# Welcome screen
if not generate_button and st.session_state.generated_newsletter is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 👋 Welcome!")
        st.markdown("""
        Generate curated AI and Product Management insights for your team in seconds.
        
        **What you'll get:**
        - 🤖 Current AI trends and analysis
        - 📊 Timeless PM wisdom and frameworks
        - 🔍 Search suggestions to find real articles
        - 📧 Email-ready format
        - 📚 Archived newsletters
        
        **Configure your newsletter in the sidebar and click "Generate Newsletter"**
        """)
        
        st.info("💡 **Note:** Each insight includes search suggestions to help you find the latest articles on these topics.")

# Handle newsletter generation
if generate_button:
    with st.spinner("🔮 Generating insights... This takes about 30 seconds."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # Get current date for context
            current_date = datetime.now().strftime("%B %Y")
            
            # AI Insights prompt - focused on current trends without fake URLs
            ai_prompt = f"""You are an expert AI analyst curating in-depth insights for product managers as of {current_date}.

Generate {num_ai} comprehensive AI INSIGHTS about: {', '.join(ai_topics)}

Team context: {team_context if team_context else 'Building AI products at scale'}

For each insight, provide:
1. **title**: A compelling, specific insight title
2. **key_insight**: A DETAILED explanation (5-7 sentences) covering:
   - What the trend/development is
   - Key technical details or capabilities
   - How leading companies are approaching this
   - Specific metrics, benchmarks, or data points where relevant
   - Practical implementation considerations
3. **why_it_matters**: 2-3 sentences on strategic implications for AI product teams
4. **action_items**: 2-3 specific actions product managers should consider
5. **search_terms**: 2-3 specific search terms for deeper research
6. **recommended_sources**: 2-3 publications to explore further

Focus on:
- Developments and trends that are CURRENT and ONGOING
- Strategic implications with specific examples
- Practical considerations with concrete details
- Real companies and products (OpenAI, Anthropic, Google, Meta, etc.)
- Include specific numbers, benchmarks, or comparisons where possible

Return ONLY valid JSON array (no markdown):
[
  {{
    "title": "...",
    "key_insight": "...",
    "why_it_matters": "...",
    "action_items": ["action1", "action2"],
    "search_terms": ["term1", "term2"],
    "recommended_sources": ["Source1", "Source2"]
  }}
]"""

            ai_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": ai_prompt}]
            )
            
            ai_text = ai_response.content[0].text
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_text:
                ai_text = ai_text.split("```")[1].split("```")[0].strip()
            ai_articles = json.loads(ai_text)
            
            # PM Insights prompt - timeless frameworks and wisdom
            pm_prompt = f"""You are an expert curator of product management insights for senior PMs.

Generate {num_pm} comprehensive PM INSIGHTS about: {', '.join(pm_topics)}

For each insight, provide:
1. **title**: A compelling insight title about a framework, principle, or best practice
2. **key_insight**: A DETAILED explanation (5-7 sentences) covering:
   - What the framework/concept is and its origin
   - Step-by-step how to apply it in practice
   - Common pitfalls to avoid
   - Examples of companies or PMs who use this effectively
   - How it applies specifically to AI products
3. **why_it_matters**: 2-3 sentences on relevance to modern AI-first product management
4. **action_items**: 2-3 specific actions product managers can take this week
5. **search_terms**: 2-3 specific search terms for deeper learning
6. **recommended_sources**: 2-3 publications to explore further

Focus on:
- TIMELESS frameworks and mental models with practical depth
- Step-by-step application guidance
- Insights from respected PM thought leaders (Lenny Rachitsky, Marty Cagan, Shreyas Doshi, etc.)
- Specific examples and case studies
- AI-first product management considerations

Return ONLY valid JSON array (no markdown):
[
  {{
    "title": "...",
    "key_insight": "...",
    "why_it_matters": "...",
    "action_items": ["action1", "action2"],
    "search_terms": ["term1", "term2"],
    "recommended_sources": ["Source1", "Source2"]
  }}
]"""

            pm_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": pm_prompt}]
            )
            
            pm_text = pm_response.content[0].text
            if "```json" in pm_text:
                pm_text = pm_text.split("```json")[1].split("```")[0].strip()
            elif "```" in pm_text:
                pm_text = pm_text.split("```")[1].split("```")[0].strip()
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
    
    # Action buttons
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
            search_terms = article.get('search_terms', [])
            sources = article.get('recommended_sources', [])
            action_items = article.get('action_items', [])
            
            email_content += f"""{i}. {article['title']}

{article['key_insight']}

💡 Why it matters: {article['why_it_matters']}

"""
            if action_items:
                email_content += "🎯 Action Items:\n"
                for action in action_items:
                    email_content += f"   • {action}\n"
                email_content += "\n"
            
            email_content += f"""🔍 Learn more: {', '.join(search_terms) if search_terms else 'N/A'}
📚 Sources: {', '.join(sources) if sources else 'N/A'}

"""
        
        email_content += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PRODUCT MANAGEMENT INSIGHTS

"""
        for i, article in enumerate(newsletter['pm_articles'], 1):
            search_terms = article.get('search_terms', [])
            sources = article.get('recommended_sources', [])
            action_items = article.get('action_items', [])
            
            email_content += f"""{i}. {article['title']}

{article['key_insight']}

💡 Why it matters: {article['why_it_matters']}

"""
            if action_items:
                email_content += "🎯 Action Items:\n"
                for action in action_items:
                    email_content += f"   • {action}\n"
                email_content += "\n"
            
            email_content += f"""🔍 Learn more: {', '.join(search_terms) if search_terms else 'N/A'}
📚 Sources: {', '.join(sources) if sources else 'N/A'}

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
            height=500
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
    
    # Show archive
    elif st.session_state.get('show_archive', False):
        st.markdown("## 📚 Newsletter Archive")
        st.markdown(f"*{len(st.session_state.newsletters)} newsletters generated*")
        st.markdown("---")
        
        for idx, past_newsletter in enumerate(st.session_state.newsletters):
            with st.expander(
                f"📰 {past_newsletter['date']}",
                expanded=(idx == 0)
            ):
                st.markdown(f"*Generated: {datetime.fromisoformat(past_newsletter['timestamp']).strftime('%B %d, %Y at %I:%M %p')}*")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🤖 AI Insights")
                    for i, article in enumerate(past_newsletter['ai_articles'], 1):
                        st.markdown(f"**{i}. {article['title']}**")
                        st.caption(article.get('key_insight', article.get('tldr', '')))
                        st.markdown("")
                
                with col2:
                    st.markdown("### 📊 PM Insights")
                    for i, article in enumerate(past_newsletter['pm_articles'], 1):
                        st.markdown(f"**{i}. {article['title']}**")
                        st.caption(article.get('key_insight', article.get('tldr', '')))
                        st.markdown("")
                
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    st.session_state.newsletters.pop(idx)
                    if len(st.session_state.newsletters) == 0:
                        st.session_state.generated_newsletter = None
                        st.session_state.show_archive = False
                    st.rerun()
        
        if st.button("⬅️ Back to Current", use_container_width=True):
            st.session_state.show_archive = False
            st.rerun()
    
    # Default: Preview
    else:
        st.markdown(f"# 📰 {newsletter['date']}")
        st.markdown("*Curated insights with search suggestions to find the latest articles*")
        st.markdown("")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h2 class="section-header">🤖 AI Insights</h2>', unsafe_allow_html=True)
            st.markdown("*Current trends and strategic considerations*")
            st.markdown("")
            
            for i, article in enumerate(newsletter['ai_articles'], 1):
                search_terms = article.get('search_terms', [])
                sources = article.get('recommended_sources', [])
                action_items = article.get('action_items', [])
                
                st.markdown(f"""
                <div class="article-card">
                    <h3>{i}. {article['title']}</h3>
                    <p style="line-height: 1.7;">{article.get('key_insight', article.get('tldr', ''))}</p>
                    <p style="color: #667eea; margin-top: 1rem;"><strong>💡 Why it matters:</strong> {article.get('why_it_matters', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if action_items:
                    st.markdown("**🎯 Action Items:**")
                    for action in action_items:
                        st.markdown(f"• {action}")
                
                if search_terms:
                    search_links = " | ".join([f'<a href="https://www.google.com/search?q={term.replace(" ", "+")}" target="_blank">{term}</a>' for term in search_terms])
                    st.markdown(f"""
                    <div class="search-tip">
                        🔍 <strong>Learn more:</strong> {search_links}<br>
                        📚 <strong>Sources:</strong> {', '.join(sources) if sources else 'TechCrunch, The Verge, VentureBeat'}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")
        
        with col2:
            st.markdown('<h2 class="section-header">📊 PM Insights</h2>', unsafe_allow_html=True)
            st.markdown("*Timeless wisdom for product leaders*")
            st.markdown("")
            
            for i, article in enumerate(newsletter['pm_articles'], 1):
                search_terms = article.get('search_terms', [])
                sources = article.get('recommended_sources', [])
                action_items = article.get('action_items', [])
                
                st.markdown(f"""
                <div class="article-card">
                    <h3>{i}. {article['title']}</h3>
                    <p style="line-height: 1.7;">{article.get('key_insight', article.get('tldr', ''))}</p>
                    <p style="color: #667eea; margin-top: 1rem;"><strong>💡 Why it matters:</strong> {article.get('why_it_matters', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if action_items:
                    st.markdown("**🎯 Action Items:**")
                    for action in action_items:
                        st.markdown(f"• {action}")
                
                if search_terms:
                    search_links = " | ".join([f'<a href="https://www.google.com/search?q={term.replace(" ", "+")}" target="_blank">{term}</a>' for term in search_terms])
                    st.markdown(f"""
                    <div class="search-tip">
                        🔍 <strong>Learn more:</strong> {search_links}<br>
                        📚 <strong>Sources:</strong> {', '.join(sources) if sources else "Lenny's Newsletter, First Round Review"}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built with ❤️ using Claude & Streamlit | Created by Udit Mehrotra</p>
    <p style="font-size: 0.9rem;">Part of the AI-First PM Study Plan</p>
</div>
""", unsafe_allow_html=True)
