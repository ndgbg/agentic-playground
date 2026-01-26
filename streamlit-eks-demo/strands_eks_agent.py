"""
Strands Agent integration for EKS operations
"""
import boto3
import json
from typing import Dict, List, Optional, Any


class StrandsEKSAgent:
    """
    Strands agent wrapper for AWS EKS operations.
    Provides natural language interface to EKS cluster management.
    """
    
    def __init__(self, region: str = 'us-west-2', access_key: str = None, secret_key: str = None):
        self.region = region
        
        if access_key and secret_key:
            self.session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        else:
            self.session = boto3.Session(region_name=region)
        
        self.eks_client = self.session.client('eks')
        self.ec2_client = self.session.client('ec2')
        self.ecr_client = self.session.client('ecr')
        
    def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task using natural language description.
        
        Args:
            task: Natural language description of the task
            context: Additional context for the task
            
        Returns:
            Dict with status and results
        """
        task_lower = task.lower()
        context = context or {}
        
        # Route to appropriate handler
        if 'list' in task_lower and 'cluster' in task_lower:
            return self.list_clusters()
        elif 'describe' in task_lower and 'cluster' in task_lower:
            return self.describe_cluster(context.get('cluster_name'))
        elif 'create' in task_lower and 'cluster' in task_lower:
            return self.create_cluster_plan(context)
        elif 'list' in task_lower and ('pod' in task_lower or 'deployment' in task_lower):
            return self.list_workloads(context.get('cluster_name'))
        elif 'health' in task_lower or 'status' in task_lower:
            return self.check_cluster_health(context.get('cluster_name'))
        else:
            return {
                'status': 'error',
                'message': f'Task not recognized: {task}',
                'suggestions': [
                    'List all EKS clusters',
                    'Describe cluster <name>',
                    'Check cluster health',
                    'List pods in cluster'
                ]
            }
    
    def list_clusters(self) -> Dict[str, Any]:
        """List all EKS clusters in the region."""
        try:
            response = self.eks_client.list_clusters()
            clusters = response.get('clusters', [])
            
            return {
                'status': 'success',
                'task': 'list_clusters',
                'data': {
                    'clusters': clusters,
                    'count': len(clusters),
                    'region': self.region
                },
                'message': f'Found {len(clusters)} cluster(s) in {self.region}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'task': 'list_clusters',
                'message': str(e)
            }
    
    def describe_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific cluster."""
        if not cluster_name:
            return {
                'status': 'error',
                'message': 'Cluster name is required'
            }
        
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            cluster = response.get('cluster', {})
            
            return {
                'status': 'success',
                'task': 'describe_cluster',
                'data': {
                    'name': cluster.get('name'),
                    'status': cluster.get('status'),
                    'version': cluster.get('version'),
                    'endpoint': cluster.get('endpoint'),
                    'created_at': str(cluster.get('createdAt')),
                    'platform_version': cluster.get('platformVersion'),
                    'vpc_config': cluster.get('resourcesVpcConfig', {})
                },
                'message': f'Cluster {cluster_name} is {cluster.get("status")}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'task': 'describe_cluster',
                'message': str(e)
            }
    
    def create_cluster_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a plan for creating an EKS cluster.
        Does not actually create the cluster, returns the plan.
        """
        cluster_name = context.get('cluster_name', 'my-eks-cluster')
        node_type = context.get('node_type', 't3.medium')
        node_count = context.get('node_count', 2)
        
        plan = {
            'cluster_name': cluster_name,
            'region': self.region,
            'kubernetes_version': '1.28',
            'node_groups': [{
                'name': f'{cluster_name}-nodes',
                'instance_type': node_type,
                'desired_capacity': node_count,
                'min_size': 1,
                'max_size': node_count + 2
            }],
            'vpc_config': {
                'create_new_vpc': True,
                'nat_gateway': True
            },
            'estimated_time': '15-20 minutes',
            'estimated_cost': f'~${0.10 + (node_count * 0.04)}/hour'
        }
        
        return {
            'status': 'success',
            'task': 'create_cluster_plan',
            'data': plan,
            'message': f'Cluster creation plan generated for {cluster_name}',
            'next_steps': [
                'Review the plan',
                'Confirm to proceed with creation',
                'Monitor creation progress'
            ]
        }
    
    def list_workloads(self, cluster_name: str) -> Dict[str, Any]:
        """List workloads (pods, deployments) in a cluster."""
        if not cluster_name:
            return {
                'status': 'error',
                'message': 'Cluster name is required'
            }
        
        return {
            'status': 'info',
            'task': 'list_workloads',
            'message': 'Kubernetes API access required',
            'instructions': [
                f'Update kubeconfig: aws eks update-kubeconfig --name {cluster_name} --region {self.region}',
                'Then use: kubectl get pods --all-namespaces'
            ]
        }
    
    def check_cluster_health(self, cluster_name: str) -> Dict[str, Any]:
        """Check the health status of a cluster."""
        if not cluster_name:
            return {
                'status': 'error',
                'message': 'Cluster name is required'
            }
        
        try:
            cluster_info = self.describe_cluster(cluster_name)
            
            if cluster_info['status'] != 'success':
                return cluster_info
            
            cluster_data = cluster_info['data']
            status = cluster_data.get('status')
            
            health = {
                'cluster_name': cluster_name,
                'status': status,
                'healthy': status == 'ACTIVE',
                'version': cluster_data.get('version'),
                'endpoint_accessible': bool(cluster_data.get('endpoint'))
            }
            
            return {
                'status': 'success',
                'task': 'check_cluster_health',
                'data': health,
                'message': f'Cluster is {"healthy" if health["healthy"] else "not healthy"}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'task': 'check_cluster_health',
                'message': str(e)
            }
    
    def get_available_tasks(self) -> List[str]:
        """Return list of available tasks this agent can perform."""
        return [
            "List all EKS clusters",
            "Describe cluster details",
            "Create cluster plan",
            "Check cluster health",
            "List workloads in cluster",
            "Get cluster status"
        ]
