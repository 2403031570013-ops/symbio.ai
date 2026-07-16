"""Initial migration for new features

Revision ID: 001
Revises: 
Create Date: 2026-07-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # AI Recommendations
    op.create_table(
        'ai_recommendations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('recommendation_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('expected_benefit', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'demand_predictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('material_id', sa.String(), nullable=False),
        sa.Column('prediction_period', sa.String(), nullable=False),
        sa.Column('predicted_demand', sa.Float(), nullable=False),
        sa.Column('confidence_interval', sa.JSON(), nullable=True),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('prediction_date', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ESG & Sustainability
    op.create_table(
        'carbon_footprints',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('factory_id', sa.String(), nullable=False),
        sa.Column('material_id', sa.String(), nullable=True),
        sa.Column('emission_source', sa.String(), nullable=False),
        sa.Column('co2_emitted', sa.Float(), nullable=False),
        sa.Column('baseline_co2', sa.Float(), nullable=True),
        sa.Column('reduction_percentage', sa.Float(), nullable=True),
        sa.Column('calculation_method', sa.String(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'esg_scores',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('factory_id', sa.String(), nullable=False),
        sa.Column('environmental_score', sa.Float(), nullable=False),
        sa.Column('social_score', sa.Float(), nullable=False),
        sa.Column('governance_score', sa.Float(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('rating', sa.String(), nullable=False),
        sa.Column('assessment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('next_assessment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('criteria', sa.JSON(), nullable=True),
        sa.Column('improvements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('factory_id')
    )
    
    # Supply Chain
    op.create_table(
        'route_optimizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('shipment_id', sa.String(), nullable=False),
        sa.Column('origin', sa.String(), nullable=False),
        sa.Column('destination', sa.String(), nullable=False),
        sa.Column('original_distance', sa.Float(), nullable=False),
        sa.Column('optimized_distance', sa.Float(), nullable=False),
        sa.Column('distance_saved', sa.Float(), nullable=False),
        sa.Column('original_time', sa.Float(), nullable=False),
        sa.Column('optimized_time', sa.Float(), nullable=False),
        sa.Column('time_saved', sa.Float(), nullable=False),
        sa.Column('original_cost', sa.Float(), nullable=False),
        sa.Column('optimized_cost', sa.Float(), nullable=False),
        sa.Column('cost_saved', sa.Float(), nullable=False),
        sa.Column('co2_saved', sa.Float(), nullable=False),
        sa.Column('route_coordinates', sa.JSON(), nullable=True),
        sa.Column('optimization_algorithm', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'inventories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('factory_id', sa.String(), nullable=False),
        sa.Column('material_id', sa.String(), nullable=False),
        sa.Column('current_stock', sa.Float(), nullable=False),
        sa.Column('minimum_stock', sa.Float(), nullable=False),
        sa.Column('maximum_stock', sa.Float(), nullable=False),
        sa.Column('reorder_point', sa.Float(), nullable=False),
        sa.Column('reorder_quantity', sa.Float(), nullable=False),
        sa.Column('stock_status', sa.String(), nullable=True),
        sa.Column('last_restock_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_restock_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('turnover_rate', sa.Float(), nullable=True),
        sa.Column('holding_cost', sa.Float(), nullable=True),
        sa.Column('stockout_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Compliance & Risk
    op.create_table(
        'compliance_checks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('factory_id', sa.String(), nullable=False),
        sa.Column('check_type', sa.String(), nullable=False),
        sa.Column('regulation', sa.String(), nullable=False),
        sa.Column('jurisdiction', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('compliance_score', sa.Float(), nullable=True),
        sa.Column('last_audit_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_audit_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('corrective_actions', sa.JSON(), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('auditor_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('factory_id', sa.String(), nullable=False),
        sa.Column('risk_category', sa.String(), nullable=False),
        sa.Column('risk_description', sa.Text(), nullable=False),
        sa.Column('likelihood', sa.Integer(), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('mitigation_strategies', sa.JSON(), nullable=True),
        sa.Column('owner', sa.String(), nullable=False),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('residual_risk', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Marketplace & Operations
    op.create_table(
        'dynamic_pricings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('material_id', sa.String(), nullable=False),
        sa.Column('base_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('price_change', sa.Float(), nullable=False),
        sa.Column('demand_factor', sa.Float(), nullable=False),
        sa.Column('supply_factor', sa.Float(), nullable=False),
        sa.Column('competitor_pricing', sa.JSON(), nullable=True),
        sa.Column('seasonality_factor', sa.Float(), nullable=True),
        sa.Column('urgency_factor', sa.Float(), nullable=True),
        sa.Column('algorithm', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('effective_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('effective_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'smart_notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('notification_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('action_required', sa.Boolean(), nullable=True),
        sa.Column('action_url', sa.String(), nullable=True),
        sa.Column('action_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'workflow_automations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger_type', sa.String(), nullable=False),
        sa.Column('trigger_conditions', sa.JSON(), nullable=True),
        sa.Column('actions', sa.JSON(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('execution_count', sa.Integer(), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('failure_count', sa.Integer(), nullable=True),
        sa.Column('last_executed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_execution', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('workflow_automations')
    op.drop_table('smart_notifications')
    op.drop_table('dynamic_pricings')
    op.drop_table('risk_assessments')
    op.drop_table('compliance_checks')
    op.drop_table('inventories')
    op.drop_table('route_optimizations')
    op.drop_table('esg_scores')
    op.drop_table('carbon_footprints')
    op.drop_table('demand_predictions')
    op.drop_table('ai_recommendations')
