"""
PharmaSim 60-Second Promo Video
Professional animated introduction for global audience
"""

from manim import *
import numpy as np
import random

# ═══════════════════════════════════════
# Color Palette - Neon Tech Theme
# ═══════════════════════════════════════
BG = "#0A0E1A"
CYAN = "#06B6D4"
GREEN = "#10B981"
PURPLE = "#8B5CF6"
ORANGE = "#F59E0B"
RED = "#EF4444"
WHITE = "#E2E8F0"
DIM = "#64748B"
MONO = "Menlo"


# ═══════════════════════════════════════
# Scene 1: Title with Particle Network
# ═══════════════════════════════════════
class Scene1_Title(Scene):
    def construct(self):
        self.camera.background_color = BG

        # Create particle network background
        particles = VGroup()
        num_particles = 60
        random.seed(42)
        
        for _ in range(num_particles):
            x = random.uniform(-7, 7)
            y = random.uniform(-4, 4)
            dot = Dot(point=[x, y, 0], radius=0.03, color=CYAN)
            dot.set_opacity(random.uniform(0.2, 0.6))
            particles.add(dot)
        
        # Draw connections
        connections = VGroup()
        for i in range(num_particles):
            for j in range(i+1, num_particles):
                dist = np.linalg.norm(particles[i].get_center() - particles[j].get_center())
                if dist < 2.5:
                    line = Line(
                        particles[i].get_center(),
                        particles[j].get_center(),
                        stroke_width=0.5,
                        color=CYAN
                    )
                    line.set_opacity(0.15 * (1 - dist/2.5))
                    connections.add(line)
        
        # Animate particles and connections
        self.play(
            FadeIn(particles, run_time=1),
            Create(connections, run_time=1.5, lag_ratio=0.01)
        )
        self.wait(0.5)
        
        # Title
        title = Text("PharmaSim", font_size=72, font=MONO, weight=BOLD, color=WHITE)
        subtitle = Text("AI-Powered Drug Launch Simulation", font_size=24, font=MONO, color=CYAN)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        self.play(
            Write(title, run_time=1.5),
            FadeIn(subtitle, shift=UP, run_time=1)
        )
        self.wait(1.5)
        
        # Fade everything out
        self.play(
            FadeOut(Group(particles, connections, title, subtitle)),
            run_time=0.8
        )


# ═══════════════════════════════════════
# Scene 2: Problem Statement
# ═══════════════════════════════════════
class Scene2_Problem(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        # Big stat
        stat = Text("90%", font_size=120, font=MONO, weight=BOLD, color=RED)
        of_drugs = Text("of drug launches", font_size=36, font=MONO, color=WHITE)
        fail = Text("underperform expectations", font_size=36, font=MONO, color=DIM)
        
        of_drugs.next_to(stat, DOWN, buff=0.3)
        fail.next_to(of_drugs, DOWN, buff=0.15)
        
        self.play(Write(stat), run_time=1)
        self.play(FadeIn(of_drugs, shift=UP), run_time=0.5)
        self.play(FadeIn(fail, shift=UP), run_time=0.5)
        self.wait(1.5)
        
        # Why?
        why = Text("Why?", font_size=64, font=MONO, weight=BOLD, color=ORANGE)
        why.move_to([0, 0, 0])
        
        reasons = VGroup(
            Text("• Unclear market dynamics", font_size=24, font=MONO, color=WHITE),
            Text("• Unpredictable physician behavior", font_size=24, font=MONO, color=WHITE),
            Text("• Complex insurance negotiations", font_size=24, font=MONO, color=WHITE),
            Text("• Patient adoption uncertainty", font_size=24, font=MONO, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        reasons.next_to(why, DOWN, buff=0.8)
        
        self.play(
            FadeOut(Group(stat, of_drugs, fail)),
            Write(why, run_time=0.8)
        )
        self.wait(0.5)
        
        for r in reasons:
            self.play(FadeIn(r, shift=RIGHT), run_time=0.4)
        self.wait(1)
        
        self.play(FadeOut(Group(why, reasons)), run_time=0.6)


# ═══════════════════════════════════════
# Scene 3: Solution - 1,801 Agents
# ═══════════════════════════════════════
class Scene3_Solution(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        # Solution headline
        headline = Text("What if you could simulate", font_size=32, font=MONO, color=DIM)
        headline2 = Text("the entire market first?", font_size=48, font=MONO, weight=BOLD, color=WHITE)
        headline2.next_to(headline, DOWN, buff=0.3)
        
        self.play(FadeIn(headline, shift=UP), run_time=0.5)
        self.play(Write(headline2), run_time=1)
        self.wait(1)
        
        # Agent count - big reveal
        self.play(FadeOut(Group(headline, headline2)), run_time=0.5)
        
        count = Text("1,801", font_size=96, font=MONO, weight=BOLD, color=CYAN)
        ai_agents = Text("AI Agents", font_size=36, font=MONO, color=WHITE)
        ai_agents.next_to(count, DOWN, buff=0.3)
        
        self.play(
            GrowFromCenter(count),
            run_time=1
        )
        self.play(FadeIn(ai_agents, shift=UP), run_time=0.5)
        self.wait(1.5)
        
        self.play(FadeOut(Group(count, ai_agents)), run_time=0.5)


# ═══════════════════════════════════════
# Scene 4: Agent Types with Network
# ═══════════════════════════════════════
class Scene4_AgentTypes(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        title = Text("Three Agent Types", font_size=36, font=MONO, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        
        # Create agent visualization
        random.seed(123)
        
        # Doctor agents (left cluster)
        doctors = VGroup()
        for i in range(15):
            x = random.uniform(-5.5, -3.5)
            y = random.uniform(-2, 2)
            dot = Dot(point=[x, y, 0], radius=0.08, color="#3B82F6")
            doctors.add(dot)
        
        # Patient agents (center cluster)
        patients = VGroup()
        for i in range(25):
            x = random.uniform(-1, 1.5)
            y = random.uniform(-2.5, 2.5)
            c = random.choice([GREEN, ORANGE, RED])
            dot = Dot(point=[x, y, 0], radius=0.06, color=c)
            patients.add(dot)
        
        # Expert agents (right cluster)
        experts = VGroup()
        for i in range(15):
            x = random.uniform(3.5, 5.5)
            y = random.uniform(-2, 2)
            dot = Dot(point=[x, y, 0], radius=0.08, color=PURPLE)
            experts.add(dot)
        
        all_agents = VGroup(doctors, patients, experts)
        
        # Draw connections
        connections = VGroup()
        all_dots = list(doctors) + list(patients) + list(experts)
        for i in range(len(all_dots)):
            for j in range(i+1, len(all_dots)):
                dist = np.linalg.norm(all_dots[i].get_center() - all_dots[j].get_center())
                if dist < 2.8:
                    line = Line(
                        all_dots[i].get_center(),
                        all_dots[j].get_center(),
                        stroke_width=0.6,
                        color=WHITE
                    )
                    line.set_opacity(0.12 * (1 - dist/2.8))
                    connections.add(line)
        
        # Labels
        doc_label = Text("400\nDoctors", font_size=18, font=MONO, color="#3B82F6", line_spacing=1)
        doc_label.move_to([-4.5, 2.8, 0])
        
        pat_label = Text("1,000\nPatients", font_size=18, font=MONO, color=GREEN, line_spacing=1)
        pat_label.move_to([0, 3, 0])
        
        exp_label = Text("400\nExperts", font_size=18, font=MONO, color=PURPLE, line_spacing=1)
        exp_label.move_to([4.5, 2.8, 0])
        
        # Animate
        self.play(
            Create(connections, run_time=1.5, lag_ratio=0.02),
            FadeIn(doctors, run_time=1),
            FadeIn(patients, run_time=1),
            FadeIn(experts, run_time=1),
        )
        self.play(
            FadeIn(doc_label, shift=DOWN),
            FadeIn(pat_label, shift=DOWN),
            FadeIn(exp_label, shift=DOWN),
            run_time=0.5
        )
        self.wait(2)
        
        # Network label
        network_label = Text(
            "Watts-Strogatz Small-World Network",
            font_size=20, font=MONO, color=DIM
        )
        network_label.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(network_label), run_time=0.5)
        self.wait(1.5)
        
        self.play(FadeOut(Group(title, all_agents, connections, doc_label, pat_label, exp_label, network_label)), run_time=0.6)


# ═══════════════════════════════════════
# Scene 5: 7-Dimension Radar Chart
# ═══════════════════════════════════════
class Scene5_Evaluation(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        title = Text("7-Dimension Expert Evaluation", font_size=36, font=MONO, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        
        # Create radar chart manually
        center = ORIGIN + DOWN * 0.3
        radius = 2.5
        n_dims = 7
        dims = ["Epidemiology", "Clinical", "Market", "Pricing", 
                "Pharmacology", "PharmaEcon", "Insurance"]
        
        # Draw axes
        axes = VGroup()
        labels = VGroup()
        for i in range(n_dims):
            angle = PI/2 - i * 2*PI/n_dims
            end = center + radius * np.array([np.cos(angle), np.sin(angle), 0])
            axis = Line(center, end, stroke_width=1, color=DIM)
            axis.set_opacity(0.4)
            axes.add(axis)
            
            label_pos = center + (radius + 0.6) * np.array([np.cos(angle), np.sin(angle), 0])
            label = Text(dims[i][:7], font_size=14, font=MONO, color=WHITE)
            label.move_to(label_pos)
            labels.add(label)
        
        # Draw rings
        rings = VGroup()
        for r in [0.5, 1.0, 1.5, 2.0, 2.5]:
            ring = Circle(radius=r, color=DIM, stroke_width=0.5)
            ring.move_to(center)
            ring.set_opacity(0.2)
            rings.add(ring)
        
        self.play(
            Create(axes, run_time=1),
            Create(rings, run_time=0.8),
            FadeIn(labels, run_time=0.8),
        )
        
        # Animate radar polygon
        scores = [0.75, 0.82, 0.68, 0.71, 0.65, 0.58, 0.73]
        points = []
        for i in range(n_dims):
            angle = PI/2 - i * 2*PI/n_dims
            r = radius * scores[i]
            points.append(center + r * np.array([np.cos(angle), np.sin(angle), 0]))
        points.append(points[0])
        
        polygon = Polygon(*points, color=CYAN, fill_opacity=0.2, stroke_width=2)
        
        # Dot animation
        dots = VGroup()
        for p in points[:-1]:
            dot = Dot(p, radius=0.06, color=CYAN)
            dots.add(dot)
        
        self.play(Create(polygon, run_time=1.5), FadeIn(dots, run_time=0.5))
        self.wait(1)
        
        # Score label
        score_text = Text("Overall: 0.704", font_size=28, font=MONO, weight=BOLD, color=GREEN)
        score_text.to_edge(DOWN, buff=0.8)
        self.play(Write(score_text), run_time=0.5)
        self.wait(1.5)
        
        self.play(FadeOut(Group(title, axes, rings, labels, polygon, dots, score_text)), run_time=0.6)


# ═══════════════════════════════════════
# Scene 6: Results & Forecast
# ═══════════════════════════════════════
class Scene6_Results(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        title = Text("24-Month Market Forecast", font_size=36, font=MONO, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        
        # Create simple chart
        axes_group = Axes(
            x_range=[0, 24, 6],
            y_range=[0, 100, 25],
            x_length=8,
            y_length=4,
            axis_config={"color": DIM, "stroke_width": 1},
            tips=False,
        ).shift(DOWN * 0.3)
        
        x_label = Text("Months", font_size=16, font=MONO, color=DIM)
        x_label.next_to(axes_group.x_axis, RIGHT)
        y_label = Text("Prescriptions/Month (K)", font_size=16, font=MONO, color=DIM)
        y_label.next_to(axes_group.y_axis, UP)
        
        self.play(Create(axes_group, run_time=1), FadeIn(x_label), FadeIn(y_label))
        
        # Create curve
        curve_points = [
            axes_group.coords_to_point(0, 0),
            axes_group.coords_to_point(3, 15),
            axes_group.coords_to_point(6, 35),
            axes_group.coords_to_point(9, 55),
            axes_group.coords_to_point(12, 72),
            axes_group.coords_to_point(15, 82),
            axes_group.coords_to_point(18, 85),
            axes_group.coords_to_point(21, 83),
            axes_group.coords_to_point(24, 80),
        ]
        
        curve = VMobject(color=CYAN, stroke_width=3)
        curve.set_points_smoothly(curve_points)
        
        # Confidence band
        upper = [
            axes_group.coords_to_point(0, 2),
            axes_group.coords_to_point(6, 42),
            axes_group.coords_to_point(12, 80),
            axes_group.coords_to_point(18, 95),
            axes_group.coords_to_point(24, 92),
        ]
        lower = [
            axes_group.coords_to_point(0, -2),
            axes_group.coords_to_point(6, 28),
            axes_group.coords_to_point(12, 64),
            axes_group.coords_to_point(18, 75),
            axes_group.coords_to_point(24, 68),
        ]
        
        band_points = upper + lower[::-1]
        band = Polygon(*band_points, color=CYAN, fill_opacity=0.1, stroke_width=0)
        
        self.play(Create(band, run_time=0.5), Create(curve, run_time=2))
        self.wait(1)
        
        # Peak annotation
        peak_dot = Dot(axes_group.coords_to_point(18, 85), radius=0.1, color=GREEN)
        peak_label = Text("Peak: 2,583 Rx/month", font_size=18, font=MONO, color=GREEN)
        peak_label.next_to(peak_dot, UP, buff=0.3)
        
        self.play(FadeIn(peak_dot), Write(peak_label), run_time=0.8)
        self.wait(1.5)
        
        self.play(FadeOut(Group(title, axes_group, x_label, y_label, curve, band, peak_dot, peak_label)), run_time=0.6)


# ═══════════════════════════════════════
# Scene 7: Key Stats Counter
# ═══════════════════════════════════════
class Scene7_Stats(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        # Stats grid
        stats = [
            ("1,801", "AI Agents", CYAN),
            ("7", "Expert Dimensions", PURPLE),
            ("28", "Sub-Dimensions", ORANGE),
            ("44+", "FDA Drugs", GREEN),
        ]
        
        stat_groups = VGroup()
        for value, label, color in stats:
            val_text = Text(value, font_size=48, font=MONO, weight=BOLD, color=color)
            label_text = Text(label, font_size=16, font=MONO, color=DIM)
            label_text.next_to(val_text, DOWN, buff=0.2)
            group = VGroup(val_text, label_text)
            stat_groups.add(group)
        
        stat_groups.arrange_in_grid(rows=2, cols=2, buff=1.5)
        
        # Animate each stat
        for sg in stat_groups:
            self.play(
                GrowFromCenter(sg[0]),
                FadeIn(sg[1], shift=UP),
                run_time=0.6
            )
            self.wait(0.3)
        
        self.wait(2)
        
        # Accuracy badge
        self.play(FadeOut(stat_groups), run_time=0.5)
        
        accuracy = Text("95%", font_size=96, font=MONO, weight=BOLD, color=GREEN)
        acc_label = Text("Prediction Accuracy", font_size=28, font=MONO, color=WHITE)
        acc_label.next_to(accuracy, DOWN, buff=0.3)
        
        self.play(GrowFromCenter(accuracy), run_time=1)
        self.play(FadeIn(acc_label, shift=UP), run_time=0.5)
        self.wait(1.5)
        
        self.play(FadeOut(Group(accuracy, acc_label)), run_time=0.5)


# ═══════════════════════════════════════
# Scene 8: CTA / Closing
# ═══════════════════════════════════════
class Scene8_CTA(Scene):
    def construct(self):
        self.camera.background_color = BG
        
        # Particle background again
        particles = VGroup()
        random.seed(42)
        for _ in range(40):
            x = random.uniform(-7, 7)
            y = random.uniform(-4, 4)
            dot = Dot(point=[x, y, 0], radius=0.02, color=CYAN)
            dot.set_opacity(random.uniform(0.15, 0.4))
            particles.add(dot)
        
        connections = VGroup()
        for i in range(len(particles)):
            for j in range(i+1, len(particles)):
                dist = np.linalg.norm(particles[i].get_center() - particles[j].get_center())
                if dist < 3:
                    line = Line(particles[i].get_center(), particles[j].get_center(),
                               stroke_width=0.4, color=CYAN)
                    line.set_opacity(0.1 * (1 - dist/3))
                    connections.add(line)
        
        self.play(FadeIn(particles), Create(connections, run_time=1.5, lag_ratio=0.03))
        
        # Main CTA
        pharma = Text("PharmaSim", font_size=64, font=MONO, weight=BOLD, color=WHITE)
        tagline = Text("Predict Drug Launch Success", font_size=28, font=MONO, color=CYAN)
        tagline.next_to(pharma, DOWN, buff=0.4)
        
        self.play(Write(pharma, run_time=1.2))
        self.play(FadeIn(tagline, shift=UP), run_time=0.6)
        self.wait(1)
        
        # URL
        url = Text("mokangmedical.github.io/PharmaSim", font_size=20, font=MONO, color=DIM)
        url.to_edge(DOWN, buff=1.2)
        
        cta = Text("Launch Simulator →", font_size=28, font=MONO, weight=BOLD, color=GREEN)
        cta.next_to(url, UP, buff=0.4)
        
        self.play(Write(cta), run_time=0.8)
        self.play(FadeIn(url), run_time=0.5)
        self.wait(2)
        
        # Final fade
        self.play(FadeOut(Group(particles, connections, pharma, tagline, cta, url)), run_time=1)
