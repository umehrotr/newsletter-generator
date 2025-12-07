import streamlit as st
import anthropic
import os
from datetime import datetime
import json

# Try Streamlit secrets first (for cloud), fall back to .env (for local)
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")

st.set_page_config(
    page_title="AI & PM Insights Newsletter Generator",
    page_icon="📰",
    layout="wide"
)

# Initialize session state for storing newsletters
if 'newsletters' not in st.session_state:
    st.session_state.newsletters = []

# Header
st.title("📰 AI & PM Insights Newsletter Generator")
st.markdown("*Curated insights for your team - AI trends and Product Management excellence*")
st.markdown("---")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Newsletter Settings")
    
    issue_date = st.date_input(
        "Newsletter Date",
        datetime.now()
    )
    
    st.markdown("---")
    
    st.subheader("🎯 Content Focus")
    
    ai_focus = st.multiselect(
        "AI Topics",
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
        default=["Generative AI / LLMs", "Multilingual AI", "AI Product Strategy"]
    )
    
    pm_focus = st.multiselect(
        "PM Topics",
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
        default=["AI-First Product Management", "Product Strategy", "Team Leadership"]
    )
    
    st.markdown("---")
    
    team_context = st.text_area(
        "Team Context (optional)",
        placeholder="E.g., We're building multilingual AI experiences for Amazon customers...",
        height=100
    )

# Main content area
tab1, tab2, tab3 = st.tabs(["📝 Generate Newsletter", "📚 Archive", "📋 Copy to Email"])

with tab1:
    st.header("Generate Bi-Weekly Newsletter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 AI Insights")
        st.markdown("Latest trends and developments in AI")
        num_ai_articles = st.slider("Number of AI articles", 1, 3, 2, key="ai_count")
    
    with col2:
        st.subheader("📊 PM Insights")
        st.markdown("Timeless wisdom for effective product management")
        num_pm_articles = st.slider("Number of PM articles", 1, 3, 2, key="pm_count")
    
    st.markdown("---")
    
    if st.button("🚀 Generate Newsletter", type="primary", use_container_width=True):
        with st.spinner("Researching and curating insights... This may take a minute."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                
                # Generate AI Insights section
                ai_prompt = f"""You are a curator of AI insights for a product management team at Amazon working on multilingual AI experiences.

Generate {num_ai_articles} high-quality article recommendations for AI insights.

Focus areas: {', '.join(ai_focus)}
Team context: {team_context if team_context else 'Building AI products at scale'}

For each article, provide:
1. **Headline**: Compelling, specific title
2. **Source**: Realistic publication (TechCrunch, The Verge, VentureBeat, MIT Tech Review, etc.)
3. **URL**: Realistic URL (use actual domains like https://techcrunch.com/2024/article-slug)
4. **TLDR**: 2-3 sentences explaining key insights and why it matters for the team
5. **Why It Matters**: 1 sentence on relevance to multilingual AI/e-commerce

Focus on recent developments (last 2-3 months) and emerging trends.
Make the content highly relevant to AI product managers building customer-facing AI features.

Format as JSON array:
[
  {{
    "headline": "...",
    "source": "...",
    "url": "...",
    "tldr": "...",
    "why_it_matters": "..."
  }}
]"""

                ai_message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    messages=[{"role": "user", "content": ai_prompt}]
                )
                
                ai_response = ai_message.content[0].text
                if "```json" in ai_response:
                    ai_response = ai_response.split("```json")[1].split("```")[0].strip()
                
                ai_articles = json.loads(ai_response)
                
                # Generate PM Insights section
                pm_prompt = f"""You are a curator of product management insights for senior PMs at a major tech company.

Generate {num_pm_articles} high-quality article recommendations for PM insights.

Focus areas: {', '.join(pm_focus)}

For each article, provide:
1. **Headline**: Compelling, specific title
2. **Source**: Realistic publication (Lenny's Newsletter, First Round Review, HBR, Product School, etc.)
3. **URL**: Realistic URL (use actual domains)
4. **TLDR**: 2-3 sentences explaining key takeaways
5. **Why It Matters**: 1 sentence on relevance to AI-first product management

These should be TIMELESS insights (can be from last 6-12 months) on effective product management.
Focus on practical frameworks, mental models, and leadership approaches.
Especially valuable for PMs transitioning to AI-first product management.

Format as JSON array:
[
  {{
    "headline": "...",
    "source": "...",
    "url": "...",
    "tldr": "...",
    "why_it_matters": "..."
  }}
]"""

                pm_message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    messages=[{"role": "user", "content": pm_prompt}]
                )
                
                pm_response = pm_message.content[0].text
                if "```json" in pm_response:
                    pm_response = pm_response.split("```json")[1].split("```")[0].strip()
                
                pm_articles = json.loads(pm_response)
                
                # Store in session state
                newsletter = {
                    "date": issue_date.strftime("%B %d, %Y"),
                    "timestamp": datetime.now().isoformat(),
                    "ai_articles": ai_articles,
                    "pm_articles": pm_articles
                }
                
                st.session_state.newsletters.insert(0, newsletter)
                st.session_state.current_newsletter = newsletter
                
                st.success("✅ Newsletter generated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating newsletter: {str(e)}")
    
    # Display current newsletter if it exists
    if 'current_newsletter' in st.session_state:
        newsletter = st.session_state.current_newsletter
        
        st.markdown("---")
        st.markdown("## 📰 Preview")
        
        st.markdown(f"### Bi-Weekly Insights | {newsletter['date']}")
        st.markdown("*Curated for the North America Languages Experience Team*")
        st.markdown("")
        
        # AI Insights Section
        st.markdown("## 🤖 AI Insights")
        st.markdown("*Latest trends and developments in AI*")
        st.markdown("")
        
        for i, article in enumerate(newsletter['ai_articles'], 1):
            st.markdown(f"**{i}. [{article['headline']}]({article['url']})**")
            st.markdown(f"*Source: {article['source']}*")
            st.markdown(f"**TLDR:** {article['tldr']}")
            st.markdown(f"*Why it matters:* {article['why_it_matters']}")
            st.markdown("")
        
        st.markdown("---")
        
        # PM Insights Section
        st.markdown("## 📊 Product Management Insights")
        st.markdown("*Timeless wisdom for effective product leadership*")
        st.markdown("")
        
        for i, article in enumerate(newsletter['pm_articles'], 1):
            st.markdown(f"**{i}. [{article['headline']}]({article['url']})**")
            st.markdown(f"*Source: {article['source']}*")
            st.markdown(f"**TLDR:** {article['tldr']}")
            st.markdown(f"*Why it matters:* {article['why_it_matters']}")
            st.markdown("")
        
        st.markdown("---")
        st.markdown("*Have insights to share? Reply to this email or post in #product-ai-learning*")

with tab2:
    st.header("📚 Newsletter Archive")
    
    if st.session_state.newsletters:
        st.markdown(f"*{len(st.session_state.newsletters)} newsletters published*")
        st.markdown("---")
        
        for idx, newsletter in enumerate(st.session_state.newsletters):
            with st.expander(f"📰 {newsletter['date']}", expanded=(idx==0)):
                st.markdown(f"*Generated: {datetime.fromisoformat(newsletter['timestamp']).strftime('%B %d, %Y at %I:%M %p')}*")
                st.markdown("")
                
                # AI Section
                st.markdown("### 🤖 AI Insights")
                for i, article in enumerate(newsletter['ai_articles'], 1):
                    st.markdown(f"**{i}. [{article['headline']}]({article['url']})**")
                    st.markdown(f"{article['tldr']}")
                    st.markdown("")
                
                # PM Section
                st.markdown("### 📊 PM Insights")
                for i, article in enumerate(newsletter['pm_articles'], 1):
                    st.markdown(f"**{i}. [{article['headline']}]({article['url']})**")
                    st.markdown(f"{article['tldr']}")
                    st.markdown("")
                
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    st.session_state.newsletters.pop(idx)
                    st.rerun()
    else:
        st.info("No newsletters generated yet. Go to the 'Generate Newsletter' tab to create your first one!")

with tab3:
    st.header("📋 Copy to Email")
    
    if 'current_newsletter' in st.session_state:
        newsletter = st.session_state.current_newsletter
        
        st.markdown("**Copy and paste this into your email:**")
        
        # Generate email-friendly text
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

Have an article, tool, or insight to share? Reply to this email or post in our #product-ai-learning channel.

Happy reading!

Best,
Udit
Head of Product, North America Languages Experience"""
        
        # Display in text area for easy copying
        st.text_area(
            "Email Content",
            email_content,
            height=600,
            help="Select all (Cmd/Ctrl+A) and copy (Cmd/Ctrl+C)"
        )
        
        # Download option
        st.download_button(
            "💾 Download as Text File",
            email_content,
            file_name=f"newsletter_{newsletter['date'].replace(' ', '_').replace(',', '')}.txt",
            mime="text/plain"
        )
        
    else:
        st.info("Generate a newsletter first to get the email-ready version!")

# Footer
st.markdown("---")
st.markdown("*AI & PM Insights Newsletter Generator | Built with Claude & Streamlit*")